from api_client import MyApiClient
import pandas as pd
import os

# --- Setup ---
output_folder = "data/seasons"
os.makedirs(output_folder, exist_ok=True)

output_file = f"{output_folder}/seasons.csv"

# --- Initialize API Client ---
client = MyApiClient()

# --- Fetch Seasons ---
print("Fetching seasons list...")

endpoint = "seasons/"
params = {
    'apiid': '1002'
}

seasons = client.fetch(endpoint, params)

# --- Normalize and Save ---
df_seasons = pd.DataFrame(seasons)

# Convert start_date from JSON format to readable (optional)
import re

def extract_epoch_ms(datestr):
    match = re.search(r'/Date\((\d+)', datestr)
    if match:
        return int(match.group(1))
    else:
        return None

df_seasons['start_epoch_ms'] = df_seasons['start_date'].apply(extract_epoch_ms)
df_seasons['start_date_readable'] = pd.to_datetime(df_seasons['start_epoch_ms'], unit='ms')

df_seasons = df_seasons.sort_values('season_text', ascending=False)

# Save to CSV
df_seasons.to_csv(output_file, index=False)

print(f"✅ Saved {len(df_seasons)} seasons to {output_file}")
