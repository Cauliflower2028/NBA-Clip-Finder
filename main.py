# Central configuration for NBA Clip Finder project

# main.py
# Central configuration AND main entry point for NBA Clip Finder workflow

import subprocess
import os
from enum import Enum

class EventMsgType(Enum):
    FIELD_GOAL_MADE = 1
    FIELD_GOAL_MISSED = 2
    FREE_THROW = 3
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

# --- Settings you can change below ---
search_players = {"Stephen Curry"}  # Set of player names to search for
actions_to_find = {
    EventMsgType.FIELD_GOAL_MADE.value,
    EventMsgType.FREE_THROW.value
}  # Set of action types to find
num_clips_to_find = 10  # Number of clips to find per player

start_season = "2018-19"    # Earliest season to include
end_season   = "2022-23"    # Latest season to include

responsible_person = "Colin Lee"  # Person responsible for final clips

input_folder_raw = "Raw_Clips"    # Folder for raw clips
output_folder_final = "Final_Clips"  # Folder for final clips

import subprocess

def run_chain():
    print("Starting NBA Clip Finder workflow...")
    print("Step 1: Gathering potential links...")
    subprocess.run(["python3", "gatherer.py"])
    # gatherer.py will prompt for next steps

if __name__ == "__main__":
    run_chain()
