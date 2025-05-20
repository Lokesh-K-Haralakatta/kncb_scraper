import os
import time
import pandas as pd
import json
import random
from api_client import MyApiClient

# --- Setup ---
client = MyApiClient()
matches_df = pd.read_csv("data/match_dimension.csv")

output_folder = "data/scorecards"
os.makedirs(output_folder, exist_ok=True)

# --- Detect already-downloaded scorecards ---
existing_ids = {
    fname.replace("scorecard_", "").replace(".json", "")
    for fname in os.listdir(output_folder)
    if fname.startswith("scorecard_") and fname.endswith(".json")
}
print(f"🔍 Found {len(existing_ids)} existing scorecards.")

# --- Fetch Scorecards ---
skipped = []

for idx, row in matches_df.iterrows():
    match_id = str(row['match_id'])

    if match_id in existing_ids:
        print(f"⏭️  Skipping MatchID {match_id} (already downloaded)")
        continue

    try:
        print(f"📥 Fetching scorecard for MatchID {match_id}...")
        scorecard = client.fetch_scorecard(match_id)

        if scorecard:
            filename = os.path.join(output_folder, f"scorecard_{match_id}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(scorecard, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {filename}")
        else:
            print(f"⚠️ No data for MatchID {match_id}")
            skipped.append((match_id, "No data"))

    except Exception as e:
        print(f"❌ Error fetching MatchID {match_id}: {e}")
        skipped.append((match_id, str(e)))

    time.sleep(random.uniform(0.7, 1.5))  # Polite scraping

# --- Save Skipped ---
if skipped:
    skipped_df = pd.DataFrame(skipped, columns=["MatchID", "Error"])
    skipped_df.to_csv("data/skipped_scorecards.csv", index=False)
    print("📄 Saved skipped scorecards to data/skipped_scorecards.csv")

print("🏁 Finished fetching all scorecards.")
