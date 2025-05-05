import pandas as pd
import os

# --- Settings ---
input_folder = "../Data/ball_by_ball"
output_folder = "../outputs"
os.makedirs(output_folder, exist_ok=True)

print(f"Input folder: {os.path.abspath(input_folder)}")

output_file = f"{output_folder}/fact_ball_events.csv"

# --- Merge All Ball-By-Ball Files ---
print("Merging ball-by-ball innings...")

# Find all ball-by-ball CSVs
input_files = [os.path.join(input_folder, f) 
               for f in os.listdir(input_folder) 
               if f.endswith(".csv")]

print(f"Found {len(input_files)} innings files to merge.")

# Load and concatenate
dataframes = []

for file in input_files:
    df = pd.read_csv(file)
    dataframes.append(df)

# Concatenate into one master DataFrame
fact_ball_events = pd.concat(dataframes, ignore_index=True)

print(f"Total deliveries after merge: {len(fact_ball_events)}")

# --- Save Master File ---
fact_ball_events.to_csv(output_file, index=False)
print(f"✅ Saved merged FactBallEvents to {output_file}")
