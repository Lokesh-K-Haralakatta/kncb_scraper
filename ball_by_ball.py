import pandas as pd
import os
import time
import json
import re
from datetime import datetime
from api_client import MyApiClient

# --- Helper Functions ---
def parse_ms_date(ms_date_str):
    """Parse /Date(1716647265000+0100)/ into Python datetime."""
    if ms_date_str:
        match = re.search(r'/Date\((\d+)', ms_date_str)
        if match:
            timestamp_ms = int(match.group(1))
            return datetime.utcfromtimestamp(timestamp_ms / 1000)
    return None

def flatten_ball(ball, match_id):
    """Flatten a single ball event."""
    return {
        "MatchID": match_id,
        "ResultID": ball.get("result_id"),
        "InningsNumber": ball.get("innings_number"),
        "OverNumber": ball.get("over_no"),
        "BallNumberInOver": ball.get("ball_no_disp"),
        "BallTimestamp": parse_ms_date(ball.get("ball_time")),
        "BatterID": ball.get("batter_id"),
        "NonStrikerID": ball.get("batter_id_ns"),
        "BowlerID": ball.get("bowler_id"),
        "RunsBatsman": ball.get("runs_bat"),
        "RunsExtras": ball.get("runs_extra"),
        "RunsTotal": (ball.get("runs_bat") or 0) + (ball.get("runs_extra") or 0),
        "DismissedPlayerID": ball.get("dismissed_batter_id"),
        "ExtraType": ball.get("extras_type"),
        "EventDescription": ball.get("l_desc"),
    }

# --- Main Script ---
# Initialize API client
client = MyApiClient(token="P0Gndh9SBZVBlUa8qKZwiA==")

# Load match data
matches_df = pd.read_csv("data/matches_2024_topklasse.csv")  # adjust path if needed

# Output folder
output_folder = "data/ball_by_ball"
os.makedirs(output_folder, exist_ok=True)

# Track skipped matches
skipped = []

# Loop over matches
for idx, row in matches_df.iterrows():
    match_id = row['MatchID']
    home_result_id = row['HomeTeamResultID']
    away_result_id = row['AwayTeamResultID']
    
    for team_result_id in [home_result_id, away_result_id]:
        try:
            innings_number = 1  # Always 1 for one-day matches

            print(f"Fetching Match {match_id}, ResultID {team_result_id}...")

            endpoint = f"matches/{match_id}/"
            params = {
                'apiid': '1002',
                'action': 'getballs',
                'sportid': '1',
                'resultid': str(team_result_id),
                'inningsnumber': str(innings_number),
            }

            data = client.fetch(endpoint, params)

            if data:
                flattened = [flatten_ball(ball, match_id) for ball in data]
                df = pd.DataFrame(flattened)
                
                # Save per team innings
                filename = f"{output_folder}/match_{match_id}_result_{team_result_id}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved {filename} ({len(df)} deliveries)")
            else:
                print(f"No data for Match {match_id}, ResultID {team_result_id}")
                skipped.append((match_id, team_result_id, "No data"))

        except Exception as e:
            print(f"Error fetching Match {match_id}, ResultID {team_result_id}: {e}")
            skipped.append((match_id, team_result_id, str(e)))

        time.sleep(2)  # Sleep politely

# Save skipped cases for review
if skipped:
    skipped_df = pd.DataFrame(skipped, columns=["MatchID", "InningsNumber", "Error"])
    skipped_df.to_csv("data/skipped_ball_by_ball.csv", index=False)
    print(f"Saved skipped fetches to data/skipped_ball_by_ball.csv")

print("✅ Completed ball-by-ball fetching!")
