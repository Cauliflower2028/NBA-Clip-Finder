import time
import os
import pandas as pd
import requests
import random
from nba_api.stats.static import players
from nba_api.stats.endpoints import LeagueGameFinder, PlayByPlayV2
# Import all settings from main.py
from main import search_players, actions_to_find, num_clips_to_find, start_season, end_season, EventMsgType

# Processed games log
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
    video_urls = json_data.get('resultSets', {}).get('Meta', {}).get('videoUrls', [])
    if video_urls:
        return video_urls[0].get('lurl')
    return None

def get_shot_category(row):
    description = row.get('HOMEDESCRIPTION')
    if pd.isna(description):
        return None
    event_type = row.get('EVENTMSGTYPE')
    if event_type == EventMsgType.FREE_THROW.value:
        return "freethrow"
    if '3PT' in description:
        return "3points shooting"
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
target_players = [p for p in nba_players if p["full_name"] in search_players]
print(f"Found {len(target_players)} out of {len(search_players)} players.")

all_video_urls = {}
url_mappings = []

for player in target_players:
    player_id = player['id']
    player_name = player['full_name']
    clips_found = 0
    all_video_urls[player_name] = []
    print(f"\n--- Processing games for {player_name} ---")
    time.sleep(0.6 + random.uniform(0, 0.3))

    # Loop through seasons from start_season to end_season inclusive
    # Note: this expects seasons formatted like "YYYY-YY" (e.g., "2018-19")
    # You might want a helper function to generate that list
    season = start_season
    # A simple way: assume seasons increment by 1 year each
    # This is a bit naive; modify if league format changes.
    while True:
        print(f"  → Checking season {season}")
        try:
            finder = LeagueGameFinder(
                player_id_nullable=player_id,
                season_nullable=season,
                league_id_nullable='00',
                season_type_nullable='Regular Season'
            )
            games_df = finder.get_data_frames()[0]
        except Exception as e:
            print(f"❌ Failed to fetch games for {player_name}, season {season}: {e}")
            games_df = pd.DataFrame()
        if not games_df.empty:
            new_games_df = games_df[~games_df['GAME_ID'].isin(processed_games)]
            game_ids = new_games_df['GAME_ID'].unique().tolist()
        else:
            game_ids = []
        print(f"    Found {len(game_ids)} new games in season {season} to search.")
        for game_id in game_ids:
            if clips_found >= num_clips_to_find:
                break
            time.sleep(0.6 + random.uniform(0, 0.3))
            try:
                pbp = PlayByPlayV2(game_id=game_id)
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
            print(f"       -> Found {len(player_actions)} made shots/FTs. Grabbing links…")
            for idx, row in player_actions.iterrows():
                if clips_found >= num_clips_to_find:
                    break
                event_id = row['EVENTNUM']
                category = row['CATEGORY']
                time.sleep(random.uniform(0, 0.3))
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
                    print(f"           -> Success! Got MP4 link for Event {event_id}")
                    clips_found += 1
                    if clips_found % 50 == 0:
                        time.sleep(10)
        # Break out if we've reached the end season or found enough clips
        if clips_found >= num_clips_to_find:
            break
        if season == end_season:
            break
        # Compute next season string
        # Example: "2018-19" → "2019-20"
        yy = season.split('-')  # or '-'
        start_year = int(yy[0])
        next_start = start_year + 1
        next_end = next_start + 1
        season = f"{next_start}-{str(next_end)[-2:]}"  # simplistic
    print(f"Finished {player_name}, collected {clips_found} clips.")

# After looping players
for player, urls in all_video_urls.items():
    output_filename = f"{player}_potential_links.txt"
    with open(output_filename, "w") as f:
        for url in urls:
            f.write(url + "\n")
    print(f"Wrote {len(urls)} URLs for {player} to {output_filename}")

mappings_df = pd.DataFrame(url_mappings)
mappings_df.to_csv('url_mapping.csv', index=False)

print("All links have been saved.")

# Prompt to run downloader.py
if __name__ == "__main__":
    answer = input("Ready to download clips? Run downloader.py now? (y/n): ").strip().lower()
    if answer == "y":
        import subprocess
        subprocess.run(["python3", "downloader.py"])
