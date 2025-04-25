from api_client import MyApiClient
import pandas as pd

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
print("Keys in response:", matches_data.keys())
print("Sample match:", matches_data['matches'][0])

'''
# Assuming the matches are in a 'matches' key
matches_list = matches_data.get('matches', [])

df_matches = pd.DataFrame(matches_list)

# Quick preview
print(df_matches.head())

# Save for future use
df_matches.to_csv('Data/matches_2023_topklasse.csv', index=False)
'''