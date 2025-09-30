import time
import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import random
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
# num_games_to_find: Max number of recent new games to search per player.
# num_events_to_find: Max number of clips to find per game.
search_players = {"Cade Cunningham"}
actions_to_find = {
    EventMsgType.FIELD_GOAL_MADE.value,
    EventMsgType.FREE_THROWfree_throw_attempt
}
num_clips_to_find = 10

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
    try:
       json_data = r.json()
    except ValueError:
        print(f"Failed to decode JSON for game {game_id}, event {event_id}: {r.text[:200]}")
        return None
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
        return None
    
def get_processed_game_ids(filename="processed_games.log"):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return {line.strip() for line in f if line.strip()}

print("--- Gatherer Script Started ---")
processed_games = get_processed_game_ids()
print(f"Found {len(processed_games)} previously processed games to skip.")

nba_players = players.get_players()
target_players = [player for player in nba_players if player["full_name"] in search_players]

print(f"Found {len(target_players)} out of {len(search_players)} players.")

all_video_urls = {}
url_mappings = []
for player in target_players:
    player_id = player['id']
    player_name = player['full_name']
    clips_found = 0
    all_video_urls[player_name] = []
    print(f"\n--- Processing games for {player_name} ---")

    # Don't overwhelm the NBA's servers
    time.sleep(0.6 + random.uniform(0, 0.3))

    try:
        finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
        games_df = finder.get_data_frames()[0]
    except Exception as e:
        print(f"❌ Failed to fetch games for {player_name} ({player_id}): {e}")
        continue  # skip this player and move on


    new_games_df = games_df[~games_df['GAME_ID'].isin(processed_games)]
    if new_games_df.empty:
        print(f"No new games found for {player_name}.")
        continue

    game_ids = new_games_df['GAME_ID'].unique().tolist()
    print(f"Found {len(game_ids)} new games to search.")

    for i, game_id in enumerate(game_ids):
        # Don't overwhelm the NBA's servers
        time.sleep(0.6 + random.uniform(0, 0.3))
        try:
            pbp = playbyplayv2.PlayByPlayV2(game_id)
            pbp_df = pbp.get_data_frames()[0]
        except Exception as e:
            print(f"Failed PlayByPlay for game {game_id}: {e}")
            continue
        player_actions = pbp_df[
            (pbp_df['PLAYER1_ID'] == player_id) &
            (pbp_df['EVENTMSGTYPE'].isin(actions_to_find))
        ].copy()
        if player_actions.empty:
            continue
        player_actions['CATEGORY'] = player_actions.apply(get_shot_category, axis=1)
        player_actions.dropna(subset=['CATEGORY'], inplace=True)
        print(f"    -> Found {len(player_actions)} made shots/FTs. Grabbing links...")
        eventsFound = 0
        for index, row in player_actions.iterrows():
            event_id = row['EVENTNUM']
            category = row['CATEGORY']
            time.sleep(0.6 + random.uniform(0, 0.3))
            mp4_url = get_mp4_url(game_id, event_id)
            if mp4_url:
                all_video_urls[player_name].append(mp4_url)
                temp_filename = f"{game_id}_{event_id}.mp4"
                url_mappings.append({
                    "player_name": player_name,
                    "category": category,
                    "temp_filename": temp_filename,
                    "original_url": mp4_url
                })  
                print(f"        -> Success! Got MP4 link for Event {event_id}")
                clips_found += 1
                if clips_found >= num_clips_to_find:
                    break
                if clips_found % 50 == 0:
                    time.sleep(10)
        if clips_found >= num_clips_to_find:
            break

for player, urls in all_video_urls.items():
    output_filename = f"{player}_potential_links.txt"
    with open(output_filename, "w") as f:
        for url in urls:
            f.write(url + "\n")
    print(f"Wrote {len(urls)} URLs for {player} to {output_filename}")

mappings_df = pd.DataFrame(url_mappings)
mappings_df.to_csv('url_mapping.csv', index=False)

print(f"Successfully collected {len(all_video_urls)} direct MP4 links.")
print(f"All links have been saved .")