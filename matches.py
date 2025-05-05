from api_client import MyApiClient
import pandas as pd
from datetime import datetime

# Initialize client
client = MyApiClient(token="hda8CvD2yDbgfXgVGAOUvg==")  # use your correct token

# Set endpoint and parameters
endpoint = "matches/"
params = {
    'apiid': '1002',
    'seasonid': '17',    # Season 2024
    'gradeid': '71374',  # Topklasse
    'action': 'ors',
    'maxrecs': '1000',
    'strmflg': '1',
}

# Fetch the matches
matches_data = client.fetch(endpoint, params)

# Explore structure
print(type(matches_data))

# If it's a list:
if isinstance(matches_data, list):
    print(f"Got a list of {len(matches_data)} matches.")
    print("Example match:")
    print(matches_data[0])  # Print first match
elif isinstance(matches_data, dict):
    print(f"Got a dict with keys: {matches_data.keys()}")
    # For example, if matches are inside a "matches" key
    if 'matches' in matches_data:
        print(matches_data['matches'][0])
else:
    print("Unexpected data structure!")

def flatten_match(match):
    def parse_ms_date(ms_date_str):
        """Parse /Date(1716631200000+0100)/ into Python datetime."""
        import re
        match = re.search(r'/Date\((\d+)', ms_date_str)
        if match:
            timestamp_ms = int(match.group(1))
            return datetime.utcfromtimestamp(timestamp_ms / 1000)  # milliseconds to seconds
        return None
    
    home_entity_id = None
    away_entity_id = None
    home_result_id = None
    away_result_id = None

    match_teams = match.get("MatchTeams", [])
    for team in match_teams:
        if team.get("is_home"):
            home_entity_id = team.get("entity_id")
            home_result_id = team.get("result_id")
        else:
            away_entity_id = team.get("entity_id")
            away_result_id = team.get("result_id")

    return {
        "MatchID": match.get("match_id"),
        "SeasonID": match.get("season_id"),
        "GradeID": match.get("grade_id"),
        "Round": match.get("round"),
        "HomeTeamName": match.get("home_name"),
        "AwayTeamName": match.get("away_name"),
        "HomeClubEntityID": home_entity_id,
        "AwayClubEntityID": away_entity_id,
        "HomeTeamResultID": home_result_id,
        "AwayTeamResultID": away_result_id,
        "VenueName": match.get("venue_name"),
        "VenueLat": match.get("venue_lat"),
        "VenueLong": match.get("venue_long"),
        "MatchDate": parse_ms_date(match.get("date1")),
        "ResultSummary": match.get("leader_text"),
        "ScoreText": match.get("score_text"),
        "WasLiveScored": match.get("was_live_scored"),
        "MatchStatusID": match.get("status_id"),
    }

# Flatten a whole list of matches
flat_matches = [flatten_match(m) for m in matches_data]

# Turn into a DataFrame
df_matches = pd.DataFrame(flat_matches)

print(df_matches.head())

df_matches.to_csv('Data/matches_2024_topklasse.csv', index=False)

'''
# Assuming the matches are in a 'matches' key
matches_list = matches_data.get('matches', [])

df_matches = pd.DataFrame(matches_list)

# Quick preview
print(df_matches.head())

# Save for future use
df_matches.to_csv('Data/matches_2023_topklasse.csv', index=False)
'''