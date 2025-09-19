## Prerequisites

Before you begin, ensure you have the following command-line tools installed. The recommended installation method for macOS is [Homebrew](https://brew.sh/).
* **yt-dlp:** For downloading video clips.
    ```bash
    brew install yt-dlp
    ```
* **mpv:** A lightweight video player for the manual logging step.
    ```bash
    brew install mpv
    ```
* **ffmpeg:** The tool that powers the final video trimming.
    ```bash
    brew install ffmpeg
    ```

---

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Cauliflower2028/NBA-Clip-Finder](https://github.com/Cauliflower2028/NBA-Clip-Finder)
    cd Your-Repo-Name
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *Note: On Windows, the activation command is `.\venv\Scripts\activate`*

3.  **Install Python Packages:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

Before starting, you may need to edit the configuration variables at the top of these two files:
* `gatherer.py`: Set your `search_players`, `actions_to_find`, etc.
* `processor.py`: Set the `responsible_person` for the final report.

---

## Workflow & Usage

Follow these five steps in order to process your clips.

### Step 1: Gather Potential Clips (`gatherer.py`)

This script searches for new games (skipping any that have been processed before) and finds potential video clips based on your settings.

From the main project directory, run:
```bash
python gatherer.py
````

**Output:** This script appends new video URLs to `potential_links.txt` and adds their metadata to the master list in `url_mapping.csv`.

### Step 2: Manually Select Clips

This is your manual review step.

1.  Open `potential_links.txt`.
2.  Click through the URLs to review the clips on the NBA website.
3.  Copy the URLs of the clips you want to keep.
4.  Paste these chosen URLs into the **`chosen_links.txt`** file (one URL per line). You can safely overwrite this file each time you run the workflow.

### Step 3: Download Your Selections (`downloader.py`)

This script reads your selections and downloads only the clips you chose.

From the main project directory, run:

```bash
python downloader.py
```

**Output:** This downloads the videos into the `Raw_Clips/` folder and updates `processed_games.log`.

### Step 4: Log Trim Times with `mpv`

This is the high-speed manual step where you define the start and end times for each clip.

1.  **Navigate into the `Raw_Clips` folder:**
    ```bash
    cd Raw_Clips
    ```
2.  **Prepare the Playlist and Run `mpv`:**
    ```bash
    # Create a playlist of all videos in the folder
    ls -1 *.mpv > playlist.txt

    # Launch the logger
    mpv --playlist=playlist.txt --script=./trim-helper.lua --keep-open=always
    ```
3.  **Use Hotkeys to Log Times:**
      * **`s`**: Set the start time.
      * **`e`**: Set the end time.
      * **`w`**: Write/update the log for the current clip.

### Step 5: Process Final Clips (`processor.py`)

This final script automates the trimming, renaming, and report generation.

1.  **Navigate back to the main project directory:**
    ```bash
    cd ..
    ```
2.  **Run the script:**
    ```bash
    python processor.py
    ```

**Output:** The script creates a `Final_Clips/` folder with your perfectly trimmed and named videos, and a `Final_Clips_Report.csv` file ready for Google Sheets.

```
```