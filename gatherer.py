import time
import requests
import subprocess
import os
import pandas as pd
import sys
import xml.etree.ElementTree as ET
from nba_api.stats.static import players
from nba_api.stats.endpoints import playbyplayv2, leaguegamefinder, videoevents
from enum import Enum

class EventMsgType(Enum):
    FIELD_GOAL_MADE = 1
    FIELD_GOAL_MISSED = 2
    FREE_THROWfree_throw_attempt = 3
    REBOUND = 4
    TURNOVER = 5
    FOUL = 6
    VIOLATION = 7
    SUBSTITUTION = 8
    TIMEOUT = 9
    JUMP_BALL = 10
    EJECTION = 11
    PERIOD_BEGIN = 12
    PERIOD_END = 13

# --- SETTINGS TO CHANGE ---
# search_players: A list of player names. Ex: {"LeBron James", "Stephen Curry"}.
# NOTE: This is very case sensitive. For example, the script will not recognize "Lebron James", but will recognize "LeBron James"
# actions_to_find: The types of plays to find. See the EventMsgType class above for all options.
# clips_per_category: Number of types of clips to find per player (3pts, 2pts, Freethrow)
search_players = {"Lonzo Ball"}
actions_to_find = {
    EventMsgType.FIELD_GOAL_MADE.value,
    EventMsgType.FREE_THROWfree_throw_attempt.value,
}
clips_per_category = 1
# Don't change this
output_folder_raw = "Raw_Clips"

def get_mp4_url(game_id, event_id):
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    
    url = f"https://stats.nba.com/stats/videoeventsasset?GameEventID={event_id}&GameID={game_id}"
    r = requests.get(url, headers=headers)
    json_data = r.json()
    
    video_urls = json_data['resultSets']['Meta']['videoUrls']
    if video_urls:
        return video_urls[0]['lurl'] # 'lurl' is the key for the high-quality MP4
    return None

def get_shot_category(row):
    description = row['HOMEDESCRIPTION']
    if pd.isna(description):
        return None
    event_type = row['EVENTMSGTYPE']
    if event_type == EventMsgType.FREE_THROWfree_throw_attempt.value:
        return "freethrow"
    if '3PT' in description:
        return "3points shooting"
    else:
        return "2points shooting"

nba_players = players.get_players()
target_players = [player for player in nba_players if player["full_name"] in search_players]

print(f"Found {len(target_players)} out of {len(search_players)} players.")

url_mappings = []

if not os.path.exists(output_folder_raw):
    print(f"Raw_Clips folder not detected. Please create a Raw_Clips folder containing the appropriate lua and txt files.")
    sys.exit(1)

for player in target_players:
    player_id = player['id']
    player_name = player['full_name']
    print(f"\n--- Finding clips for {player_name} ---")

    clip_tracker = {
        "3points shooting": clips_per_category,
        "2points shooting": clips_per_category,
        "freethrow": clips_per_category
    }

    # Don't overwhelm the NBA's servers
    time.sleep(0.6)

    finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
    games_df = finder.get_data_frames()[0]
    game_ids = games_df['GAME_ID'].unique().tolist()

    for i, game_id in enumerate(game_ids):
        if all(value == 0 for value in clip_tracker.values()):
            print(f"    -> All clips found for {player_name} met. Moving to next player.")
            break

        print(f"  -> Processing Game {i + 1} for {player_name}")

        # Don't overwhelm the NBA's servers
        time.sleep(0.6)

        pbp = playbyplayv2.PlayByPlayV2(game_id)
        pbp_df = pbp.get_data_frames()[0]
        player_actions = pbp_df[
            (pbp_df['PLAYER1_ID'] == player_id) &
            (pbp_df['EVENTMSGTYPE'].isin(actions_to_find))
        ].copy()

        if player_actions.empty:
            continue

        print(f"    -> Found {len(player_actions)} made shots/FTs. Grabbing links...")
        player_actions['CATEGORY'] = player_actions.apply(get_shot_category, axis=1)
        eventsFound = 0
        for index, row in player_actions.iterrows():
            category = row['CATEGORY']
            if category in clip_tracker and clip_tracker[category] > 0:
                event_id = row['EVENTNUM']
                mp4_url = get_mp4_url(game_id, event_id)
                if mp4_url:
                    safe_player_name = player_name.replace(" ", "_")
                    temp_filename = f"{safe_player_name}--{game_id}--{event_id}--{category}.mp4"
                    output_path = os.path.join(output_folder_raw, temp_filename)
                    print(f"    -> Downloading: {temp_filename}")
                    subprocess.run(['yt-dlp', '-q', '-o', output_path, mp4_url])
                    url_mappings.append({
                        "player_name": player_name,
                        "category": category,
                        "temp_filename": temp_filename,
                        "original_url": mp4_url
                    })
                    clip_tracker[category] -= 1
                    print(f"    -> Success! Found a clip for '{category}'")

mappings_df = pd.DataFrame(url_mappings)
mappings_df.to_csv('url_mapping.csv', index=False)

print(f"All raw clips downloaded to '{output_folder_raw}' folder.")
print("URL mapping saved to 'url_mapping.csv', ready for the trimming step.")