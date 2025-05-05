# build_include_list.py

import pandas as pd
import os

# --- Setup ---
grades_file = "data/grades/grades.csv"
output_folder = "data/include_lists"
os.makedirs(output_folder, exist_ok=True)
output_file = f"{output_folder}/include_list.csv"

# --- Load Grades ---
df_grades = pd.read_csv(grades_file)

# --- Define Inclusion Logic ---
must_have_keywords = [
    "topklasse",
    "hoofdklasse",
]

nice_to_have_keywords = [
    "eerste klasse",
    "overgangsklasse",
    "tweede klasse",
    "zami",
    "zomi",
]

def include_grade(grade_name):
    if pd.isna(grade_name):
        return False
    grade_name = grade_name.lower()

    # Always include if must have
    for keyword in must_have_keywords:
        if keyword in grade_name:
            return True

    # Include nice-to-haves
    for keyword in nice_to_have_keywords:
        if keyword in grade_name:
            return True

    return False


# --- Filter ---
df_include = df_grades[df_grades['grade_name'].apply(include_grade)].copy()

df_include = df_include[['season_id', 'season_text', 'grade_id', 'grade_name']]
df_include = df_include.sort_values(['season_id', 'grade_name'])
# --- Force correct data types ---
df_include['season_id'] = df_include['season_id'].astype(int)
df_include['season_text'] = df_include['season_text'].astype(int)
df_include['grade_id'] = df_include['grade_id'].astype(int)

# --- Save Include List ---
df_include.to_csv(output_file, index=False)

print(f"✅ Saved {len(df_include)} entries to {output_file}")
