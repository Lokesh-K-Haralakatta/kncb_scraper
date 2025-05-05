import os
import time
import pandas as pd
import json
from api_client import MyApiClient

# --- Setup ---
client = MyApiClient(token="P0Gndh9SBZVBlUa8qKZwiA==")

matches_df = pd.read_csv("data/matches_2024_topklasse.csv")
output_folder = "data/scorecards"
os.makedirs(output_folder, exist_ok=True)

# --- Fetch Scorecards ---
skipped = []

for idx, row in matches_df.iterrows():
    match_id = row['MatchID']

    try:
        print(f"Fetching scorecard for MatchID {match_id}...")

        scorecard = client.fetch_scorecard(match_id)

        if scorecard:
            filename = os.path.join(output_folder, f"scorecard_{match_id}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(scorecard, f, ensure_ascii=False, indent=2)
            print(f"Saved {filename}")
        else:
            print(f"No data for MatchID {match_id}")
            skipped.append((match_id, "No data"))

    except Exception as e:
        print(f"Error fetching MatchID {match_id}: {e}")
        skipped.append((match_id, str(e)))

    time.sleep(2)  # Sleep politely

# --- Save Skipped ---
if skipped:
    skipped_df = pd.DataFrame(skipped, columns=["MatchID", "Error"])
    skipped_df.to_csv("../data/skipped_scorecards.csv", index=False)
    print("Saved skipped scorecards list.")

print("✅ Finished fetching all scorecards.")
