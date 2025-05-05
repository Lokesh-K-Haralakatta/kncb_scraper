from api_client import MyApiClient
import pandas as pd
import os
import time
import requests
import random

# --- Settings ---
MAX_RETRIES = 2
MAX_401_ERRORS = 1

# --- Setup ---
include_file = "data/include_lists/include_list.csv"
output_folder = "data/ball_by_ball"
os.makedirs(output_folder, exist_ok=True)

# --- Build set of already downloaded files ---
existing_files = set()

for filename in os.listdir(output_folder):
    if filename.endswith("_balls.json"):
        parts = filename.split("_")
        match_id = parts[0]
        result_id = parts[2]  # result ID is the third part (matchid_result_resultid_balls.json)
        key = (match_id, result_id)
        existing_files.add(key)

print(f"🧠 Found {len(existing_files)} innings already downloaded.")

# --- Initialize API Client ---
client = MyApiClient()

# --- Load Include List ---
df_include = pd.read_csv(include_file)

# --- Helper: Fetch matches for a season and grade ---
def fetch_matches(season_id, grade_id):
    endpoint = "matches/"
    params = {
        'apiid': '1002',
        'seasonid': season_id,
        'gradeid': grade_id,
        'action': 'ors',
        'maxrecs': '1000',
        'strmflg': '1',
    }
    return client.fetch(endpoint, params)

# --- Helper: Fetch ball-by-ball for a match ---
def fetch_ball_by_ball(match_id, result_id):
    endpoint = f"matches/{match_id}/"
    params = {
        'apiid': '1002',
        'action': 'getballs',
        'sportid': '1',
        'resultid': result_id,
        'inningsnumber': '1',  # As you mentioned, all innings are '1' for one-day cricket
    }
    return client.fetch(endpoint, params)

# --- Main Loop ---
for idx, row in df_include.iterrows():
    season_id = int(row['season_id'])
    grade_id = int(row['grade_id'])
    grade_name = row['grade_name']
    season_text = row['season_text']

    print(f"📂 Fetching matches for {grade_name} {season_text}...")

    try:
        matches = fetch_matches(season_id, grade_id)
    except Exception as e:
        print(f"⚠️ Failed to fetch matches for {grade_name} {season_text}: {e}")
        continue

    print(f"✅ Found {len(matches)} matches.")

    for match in matches:
        match_id = match.get('match_id')

        unauthorized_errors_in_match = 0  # Reset for each match
        success = True

    # --- Collect result IDs ---
        result_ids = []
        if 'MatchTeams' in match and match['MatchTeams']:
            for team in match['MatchTeams']:
                if 'result_id' in team and team['result_id'] not in result_ids:
                    result_ids.append(team['result_id'])

        if not match_id or not result_ids:
            print(f"⚠️ Skipping match (missing match_id or result_id)")
            continue

        match_file_path = os.path.join(output_folder, f"{match_id}_match.json")

        # Save match metadata (only once per match)
        if not os.path.exists(match_file_path):
            pd.DataFrame([match]).to_json(match_file_path, orient="records", indent=2)
            print(f"✅ Saved match metadata for {match_id}")

        for rid in result_ids:
            key = (str(match_id), str(rid))  # match_id and result_id as strings
            balls_file_path = os.path.join(output_folder, f"{match_id}_result_{rid}_balls.json")

            # Now we can check properly
            if key in existing_files:
                print(f"📄 Skipping already downloaded match_id {match_id}, result_id {rid}")
                continue

            print(f"🎯 Fetching ball-by-ball for MatchID {match_id}, ResultID {rid}...")

            try:
                balls = fetch_ball_by_ball(match_id, rid)
                
                if balls:  # Only if there are balls fetched
                    pd.DataFrame(balls).to_json(balls_file_path, orient="records", indent=2)
                    print(f"✅ Saved {len(balls)} balls for ResultID {rid}")
                else:
                    print(f"⚠️ No ball-by-ball data for MatchID {match_id}, ResultID {rid}. Skipping file save.")
            
            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 401:
                    unauthorized_errors_in_match += 1
                    print(f"🚨 401 Unauthorized for MatchID {match_id}, ResultID {rid}!")

                    if unauthorized_errors_in_match > MAX_401_ERRORS:
                        print("🚨 Too many 401s during this match! Stopping entire script.")
                        exit(1)
                    else:
                        print("⚠️ Retrying this match after token error...")
                        success = False
                        break  # Break out of results loop and retry the whole match

                else:
                    print(f"⚠️ HTTP error ({http_err.response.status_code}) for MatchID {match_id}, ResultID {rid}: {http_err}")
                    success = False
                    break  # Something else went wrong

            except Exception as e:
                print(f"⚠️ Failed fetching balls for ResultID {rid} in MatchID {match_id}: {e}")

            sleep_time = random.uniform(0.7, 1.5)
            time.sleep(sleep_time)

        if not success:
            for attempt in range(1, MAX_RETRIES + 2):
                print(f"🔄 Retrying whole match {match_id} attempt {attempt}/{MAX_RETRIES+1}...")
                # Maybe reload result_ids?
                # Re-run this match logic again
                # (you might need to refactor match downloading into a helper function)

print("🏁 Done fetching all ball-by-ball data!")
