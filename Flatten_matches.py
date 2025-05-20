# transform/flatten_match_dimension.py
import pandas as pd
import os
import json
import re
from datetime import datetime

# --- Helper Functions ---
def parse_ms_date(ms_date_str):
    """Convert /Date(1716647265000+0100)/ to datetime."""
    if not ms_date_str:
        return None
    match = re.search(r'/Date\((\d+)', ms_date_str)
    if not match:
        return None
    ts_ms = int(match.group(1))
    return datetime.utcfromtimestamp(ts_ms / 1000)


def flatten_match_dimension(input_dir="data/ball_by_ball", output_csv="data/match_dimension.csv"):
    """
    Reads per-match JSON files and flattens nested metadata, including MatchConfig
    and MatchTeams (result_id, entity_id, team_id).
    """
    records = []
    for fname in os.listdir(input_dir):
        if not fname.endswith("_match.json"):
            continue
        path = os.path.join(input_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        if not data_list:
            continue
        m = data_list[0]

        # Base match fields
        rec = {
            'match_id': m.get('match_id'),
            'external_match_id': m.get('external_match_id'),
            'association_id': m.get('association_id'),
            'season_id': m.get('season_id'),
            'grade_id': m.get('grade_id'),
            'grade_name': m.get('grade_name'),
            'date1':   parse_ms_date(m.get('date1')),
            'date2':   parse_ms_date(m.get('date2')),
            'date3':   parse_ms_date(m.get('date3')),
            'date4':   parse_ms_date(m.get('date4')),
            'start_time1': m.get('start_time1'),
            'venue_id':     m.get('venue_id'),
            'venue_name':   m.get('venue_name'),
            'venue_address':m.get('venue_address'),
            'venue_lat':    m.get('venue_lat'),
            'venue_long':   m.get('venue_long'),
            'toss_won_by':  m.get('toss_won_by'),
            'batted_first': m.get('batted_first'),
            'allow_live_score': m.get('allow_live_score'),
            'follow_on':    m.get('follow_on'),
            'score_text':   m.get('score_text'),
            'leader_text':  m.get('leader_text'),
            'g_sort_order': m.get('g_sort_order'),
            'um_pire1':     m.get('um_pire1'),
            'um_pire2':     m.get('um_pire2'),
        }

        # Flatten MatchConfig
        cfg = m.get('MatchConfig', {})
        for k, v in cfg.items():
            rec[f'config_{k}'] = v

        # Flatten MatchTeams: can be multiple teams
        for idx, team in enumerate(m.get('MatchTeams', []), start=1):
            prefix = f'team{idx}'
            rec[f'{prefix}_is_home']   = team.get('is_home')
            rec[f'{prefix}_team_name'] = team.get('team_name')
            rec[f'{prefix}_team_id']   = team.get('team_id')
            rec[f'{prefix}_entity_id'] = team.get('entity_id')
            rec[f'{prefix}_result_id'] = team.get('result_id')
            rec[f'{prefix}_result_type'] = team.get('result_type_text')
            # Innings summary
            innings = team.get('Innings', [])
            if innings:
                inn = innings[0]
                rec[f'{prefix}_runs']         = inn.get('runs')
                rec[f'{prefix}_wickets']      = inn.get('wickets')
                rec[f'{prefix}_overs_bowled'] = inn.get('overs_bowled')
                rec[f'{prefix}_extras']       = inn.get('extras')
                rec[f'{prefix}_leg_byes']     = inn.get('leg_byes')
                rec[f'{prefix}_wides']        = inn.get('wides')
                rec[f'{prefix}_no_balls']     = inn.get('no_balls')

        records.append(rec)

    # Build DataFrame and save
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"✅ Flattened {len(df)} matches into {output_csv}")

if __name__ == '__main__':
    flatten_match_dimension()