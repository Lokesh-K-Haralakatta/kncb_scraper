# fetch_grades.py

from api_client import MyApiClient
import pandas as pd
import os
import time

# --- Setup ---
seasons_file = "data/seasons/seasons.csv"
output_folder = "data/grades"
os.makedirs(output_folder, exist_ok=True)
output_file = f"{output_folder}/grades.csv"

# --- Initialize API Client ---
client = MyApiClient()

# --- Load Seasons ---
df_seasons = pd.read_csv(seasons_file)

# --- Fetch Grades ---
all_grades = []

print("Fetching grades for each season...")

for idx, row in df_seasons.iterrows():
    season_id = row['season_id']
    season_text = str(row['season_text']).strip()

    # Skip old seasons (optional safety)
    #if int(season_text) < 2024:
    #    print(f"Skipping {season_text} (token not valid for older seasons)")
    #    continue

    print(f"Fetching grades for season {season_text} (ID {season_id})...")

    endpoint = "grades/"
    params = {
        'apiid': '1002',
        'seasonId': season_id,
    }

    try:
        grades = client.fetch(endpoint, params)

        for grade in grades:
            round_list_str = grade.get('round_list', '')
            rounds = '|'.join(round_list_str.split(',')) if round_list_str else ''

            all_grades.append({
                "season_id": season_id,
                "season_text": season_text,
                "grade_id": grade['grade_id'],
                "grade_name": grade['grade_name'],
                "grade_short_name": grade.get('grade_short_name', None),
                "sport_id": grade.get('sport_id', None),
                "gender_id": grade.get('gender_id', None),
                "agegroup_id": grade.get('agegroup_id', None),
                "association_name": grade.get('association_name', None),
                "rounds": rounds
            })

    except Exception as e:
        print(f"⚠️ Failed fetching grades for season {season_id}: {e}")

    time.sleep(2)  # Be polite to the API

# --- Save to CSV ---
df_grades = pd.DataFrame(all_grades)
df_grades = df_grades.sort_values(["season_text", "grade_name"])

df_grades.to_csv(output_file, index=False)

print(f"✅ Saved {len(df_grades)} grades to {output_file}")
