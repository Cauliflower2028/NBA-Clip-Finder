# NBA Clip Finder

This Python script automatically finds and generates direct download links for video clips of specific NBA players and plays.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Cauliflower2028/NBA-Clip-Finder.git](https://github.com/Cauliflower2028/NBA-Clip-Finder.git)
    cd NBA-Clip-Finder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the venv
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on Mac/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running, open `main.py` and edit the settings at the top of the file to choose your players, actions, and limits.

```python
# --- SETTINGS TO CHANGE ---
# search_players: A list of player names. Ex: {"LeBron James", "Stephen Curry"}.
# NOTE: This is very case sensitive. For example, the script will not recognize "Lebron James", but will recognize "LeBron James"
# actions_to_find: The types of plays to find. See the EventMsgType class above for all options.
# num_games_to_find: Max number of recent games to search per player.
# num_events_to_find: Max number of clips to find per game.