# transform/extract_dismissals.py

import os
import json
import pandas as pd

# --- Settings ---
scorecards_folder = "../data/scorecards"
output_folder = "../data/dismissals"
os.makedirs(output_folder, exist_ok=True)

output_file = f"{output_folder}/dismissals.csv"

# --- Helper Function ---
def extract_dismissals_from_scorecard(scorecard, match_id):
    dismissals = []
    match_teams = scorecard.get('MatchTeams', [])
    
    for team in match_teams:
        innings_list = team.get('Innings', [])
        for innings in innings_list:
            player_perfs = innings.get('PlayerPerfs', [])
            for perf in player_perfs:
                if perf.get('__type', '').startswith('Batting') and perf.get('dismissal_id', 0) != 0:
                    dismissals.append({
                        "MatchID": match_id,
                        "BatterID": perf.get('player_id'),
                        "DismissalID": perf.get('dismissal_id'),
                        "DismissalText": perf.get('dismissal_text'),
                        "BowlerID": perf.get('dismisser2_id'),   # Bowler (2nd dismisser)
                        "FielderID": perf.get('dismisser1_id'),  # Fielder (1st dismisser, if any)
                    })
    return dismissals

# --- Main Script ---
print("Extracting dismissals from scorecards...")

all_dismissals = []

for filename in os.listdir(scorecards_folder):
    if filename.endswith(".json"):
        match_id = int(filename.split("_")[1].split(".")[0])
        filepath = os.path.join(scorecards_folder, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            scorecard = json.load(f)

        match_dismissals = extract_dismissals_from_scorecard(scorecard, match_id)
        all_dismissals.extend(match_dismissals)

# --- Save Dismissals to CSV ---
df_dismissals = pd.DataFrame(all_dismissals)

if not df_dismissals.empty:
    df_dismissals.to_csv(output_file, index=False)
    print(f"✅ Saved {len(df_dismissals)} dismissals to {output_file}")
else:
    print("⚠️ No dismissals found.")

print("✅ Extraction complete.")
