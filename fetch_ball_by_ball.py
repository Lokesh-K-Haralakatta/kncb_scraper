from api_client import MyApiClient
import pandas as pd
import os
import time
import random
import requests

# --- Settings ---
MAX_RETRIES = 2       # how many times to retry a match after final 401
MAX_401_ERRORS = 1    # how many 401s per match before forcing a retry

# --- Setup ---
include_file = "data/include_lists/include_list.csv"
output_folder = "data/ball_by_ball"
os.makedirs(output_folder, exist_ok=True)

# --- Build set of already downloaded files ---
existing_files = set()
for filename in os.listdir(output_folder):
    if filename.endswith("_balls.json"):
        parts = filename.split("_")
        existing_files.add((parts[0], parts[2]))

print(f"🧠 Found {len(existing_files)} innings already downloaded.")

# --- Initialize API Client ---
client = MyApiClient()  # uses token_manager internally

# --- Load Include List ---
df_include = pd.read_csv(include_file)

def process_match(match, max_401=MAX_401_ERRORS):
    """Fetch all innings for one match, returns True on success."""
    match_id = match.get("match_id")
    if not match_id:
        print("⚠️  Missing match_id; skipping")
        return True

    # Extract unique result_ids
    rids = {
        t["result_id"] for t in match.get("MatchTeams", [])
        if "result_id" in t
    }
    if not rids:
        print(f"⚠️  No result_ids for match {match_id}; skipping")
        return True

    # Save match metadata once
    meta_path = os.path.join(output_folder, f"{match_id}_match.json")
    if not os.path.exists(meta_path):
        pd.DataFrame([match]).to_json(meta_path, orient="records", indent=2)
        print(f"✅ Saved metadata for match {match_id}")

    unauthorized_count = 0

    # Iterate innings
    for rid in rids:
        key = (str(match_id), str(rid))
        if key in existing_files:
            print(f"📄 Skipping already downloaded {match_id}, {rid}")
            continue

        print(f"🎯 Fetching ball-by-ball for {match_id}, result {rid}...")
        try:
            balls = client.fetch(
                f"matches/{match_id}/",
                params={
                    "apiid": "1002",
                    "action": "getballs",
                    "sportid": "1",
                    "resultid": str(rid),
                    "inningsnumber": "1",
                }
            )
            if balls:
                out = os.path.join(
                    output_folder,
                    f"{match_id}_result_{rid}_balls.json"
                )
                pd.DataFrame(balls).to_json(out, orient="records", indent=2)
                print(f"✅ Saved {len(balls)} balls to {out}")
            else:
                print(f"⚠️ No deliveries for {match_id}, {rid}; skipping file save")

        except requests.HTTPError as e:
            status = e.response.status_code
            if status == 401:
                unauthorized_count += 1
                print(f"🚨 401 Unauthorized for {match_id}, {rid}")
                if unauthorized_count > max_401:
                    # Give control back for a full match retry
                    raise e
                else:
                    print("🔄 Triggering manual refresh and retrying this match")
                    # force-refresh the token before we bail
                    client.token_manager.refresh()
                    raise e
            else:
                print(f"⚠️ HTTP {status} for {match_id}, {rid}: {e}")
                return False

        except Exception as e:
            print(f"⚠️ Error fetching deliveries for {match_id}, {rid}: {e}")
            return False

        # polite sleep
        time.sleep(random.uniform(0.7, 1.5))

    return True


# --- Main Loop ---
for idx, row in df_include.iterrows():
    season_id = int(row["season_id"])
    grade_id  = int(row["grade_id"])
    print(f"📂 Fetching matches for grade {grade_id}, season {season_id}…")

    try:
        matches = client.fetch(
            "matches/",
            params={
                "apiid":    "1002",
                "seasonid": season_id,
                "gradeid":  grade_id,
                "action":   "ors",
                "maxrecs":  "1000",
                "strmflg":  "1",
            }
        )
    except Exception as e:
        print(f"⚠️ Could not fetch match list: {e}")
        continue

    print(f"✅ Found {len(matches)} matches.")

    for match in matches:
        # Attempt up to MAX_RETRIES+1 times per match
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                success = process_match(match)
                if success:
                    break
            except requests.HTTPError as e:
                # Only unhandled 401s come here
                print(f"🔄 Retry {attempt}/{MAX_RETRIES+1} for match {match.get('match_id')}")
                continue
        else:
            print(f"🚨 All retries failed for match {match.get('match_id')}")

print("🏁 Completed all ball-by-ball fetching!")
