import subprocess
import os
import pandas as pd
from datetime import datetime

# --- Configuration ---
input_folder_raw = "Raw_Clips"
output_folder_final = "Final_Clips"
responsible_person = "Your Name Here"

def get_duration(start_str, end_str):
    time_format = '%H:%M:%S.%f'
    start_time = datetime.strptime(start_str, time_format)
    end_time = datetime.strptime(end_str, time_format)
    return (end_time - start_time).total_seconds()

print("--- Processor Script Started ---")
if not os.path.exists(output_folder_final):
    os.makedirs(output_folder_final)

cut_list_file = os.path.join(input_folder_raw, 'cut_list.txt')
master_list_file = 'url_mapping.csv'

print(f"Loading data from '{master_list_file}' and '{cut_list_file}'...")
master_df = pd.read_csv(master_list_file)
cuts_df = pd.read_csv(cut_list_file, names=['temp_filename', 'start_time', 'end_time'])
merged_df = pd.merge(master_df, cuts_df, on='temp_filename')

category_counters = {}
report_data = []

print(f"Processing {len(merged_df)} logged clips...")

for _, row in merged_df.iterrows():
    player_name = row['player_name']
    category = row['category']
    temp_filename = row['temp_filename']
    start_time_str = row['start_time']
    end_time_str = row['end_time']
    original_url = row['original_url']
    
    if player_name not in category_counters: category_counters[player_name] = {}
    if category not in category_counters[player_name]: category_counters[player_name][category] = 0
    category_counters[player_name][category] += 1
    number = category_counters[player_name][category]
    safe_player_name = player_name.replace(" ", "_")
    final_clip_name = f"{safe_player_name}_{category}_{number}.mp4"
    
    final_output_path = os.path.join(output_folder_final, final_clip_name)
    raw_input_path = os.path.join(input_folder_raw, temp_filename)

    duration_seconds = get_duration(start_time_str, end_time_str)
    print(f"  -> Trimming {temp_filename} from {start_time_str} for {duration_seconds:.2f}s -> {final_clip_name}")

    command = [
        'ffmpeg',
        '-i', raw_input_path,
        '-ss', str(start_time_str),
        '-t', str(duration_seconds),
        '-y',
        final_output_path
    ]

    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    report_data.append({
        "Player Name": player_name,
        "Video URL": original_url,
        "Clip Name": final_clip_name,
        "Responsible Person": responsible_person
    })

print("\nGenerating final CSV report...")
report_df = pd.DataFrame(report_data)
report_df.to_csv("Final_Clips_Report.csv", index=False)

print("\n--- Processor Script Complete ---")
print(f"All final clips are in '{output_folder_final}'.")
print("CSV report 'Final_Clips_Report.csv' has been generated.")