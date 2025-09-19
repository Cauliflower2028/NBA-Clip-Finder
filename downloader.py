import pandas as pd
import subprocess
import os

# --- Configuration ---
output_folder_raw = "Raw_Clips"
links_to_download_file = "chosen_links.txt"
mapping_file = "url_mapping.csv"
log_file = "processed_games.log"

def update_processed_log(game_ids_to_add):
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            existing_ids = {line.strip() for line in f if line.strip()}
    else:
        existing_ids = set()
    all_ids = existing_ids.union(game_ids_to_add)
    with open(log_file, 'w') as f:
        for gid in sorted(list(all_ids)):
            f.write(f"{gid}\n")

# --- Main Logic ---
print("--- downloader.py started ---")
master_df = pd.read_csv(mapping_file)

all_game_ids_in_mapping = set(master_df['temp_filename'].str.split('_').str[0])
update_processed_log(all_game_ids_in_mapping)
print(f"Updated '{log_file}' with all {len(all_game_ids_in_mapping)} unique game IDs from '{mapping_file}'.")

with open(links_to_download_file, 'r') as f:
    chosen_urls = {line.strip() for line in f if line.strip()}

# Filter the master list to get only the rows for the URLs you have chosen
to_download_df = master_df[master_df['original_url'].isin(chosen_urls)]

game_ids_to_log = set()
print(f"Processing {len(to_download_df)} chosen clips...")
for _, row in to_download_df.iterrows():
    temp_filename = row['temp_filename']
    original_url = row['original_url']
    output_path = os.path.join(output_folder_raw, temp_filename)
    
    if os.path.exists(output_path):
        print(f"  -> Skipping: {temp_filename} (already exists)")
    else:
        print(f"  -> Downloading: {temp_filename}")
        subprocess.run(['yt-dlp', '-q', '-o', output_path, original_url])

print("--- Downloader Script Complete ---")