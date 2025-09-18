# NBA Clip Finder & Processor

This project provides a workflow to find, download, trim, and log specific video clips of NBA players based on play-by-play data. The process is broken down into three main steps: Gathering, Logging, and Processing.

## Prerequisites

Before you begin, ensure you have the following command-line tools installed. The recommended installation method for macOS is [Homebrew](https://brew.sh/).

* **Python 3.10+**
* **Git**
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

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Cauliflower2028/NBA-Clip-Finder.git](https://github.com/Cauliflower2028/NBA-Clip-Finder.git)
    cd NBA-Clip-Finder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *Note: On Windows, the activation command is `.\venv\Scripts\activate`*

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Workflow & Usage

The process is divided into three steps. You must run them in order.

### Step 1: Gather Raw Clips (`gatherer.py`)

This script finds all potential clips based on your settings and downloads the raw, untrimmed videos into the `Raw_Clips` folder.

1.  **Configure:** Open `gatherer.py` and edit the settings at the top (e.g., `search_players`, `clips_per_category`).
2.  **Run:** From the main `NBA-Clip-Finder` directory, run the script:
    ```bash
    python gatherer.py
    ```

### Step 2: Log Trim Times (Manual `mpv` Workflow)

This is the high-speed manual step where you define the start and end times for each clip. The necessary `trim-helper.lua` script is already included in the `Raw_Clips` folder.

1.  **Navigate:** Open your terminal and cd into the `Raw_Clips` folder:
    ```bash
    cd Raw_Clips
    ```
2.  **Prepare & Run:** Generate the playlist and run the logger with these two commands:
    ```bash
    ls -1 *.mp4 > playlist.txt
    mpv --playlist=playlist.txt --script=./trim-helper.lua --keep-open=always
    ```
3.  **Use Hotkeys:**
    * **`s`**: Set start time.
    * **`e`**: Set end time.
    * **`w`**: Write/update the log for the current clip.
    * **`q`**: Quit the current video and advance to the next.

### Step 3: Process Final Clips (`processor.py`)

This final script automates the trimming, renaming, and report generation based on your `cut_list.txt`.

1.  **Navigate:** Make sure you are in the **main `NBA-Clip-Finder` directory** (not `Raw_Clips`).
    ```bash
    cd ..
    ```
2.  **Configure:** Open `processor.py` and edit the `responsible_person` variable.
3.  **Run:**
    ```bash
    python processor.py
    ```
4.  **Output:** The script will create a `Final_Clips/` folder with your perfectly trimmed and named videos, and a `Final_Clips_Report.csv` file ready for Google Sheets.