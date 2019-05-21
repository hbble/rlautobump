# RL Garage Autobump Tool (Outdated)
Rocket League Garage Autobump Tool. Not working now. Can be used as an example project.

## Installation (Locally)
1. Make sure you have installed [Python 3](https://www.python.org/downloads/) on your machine.

2. Clone repository `git clone https://github.com/hbble/rlautobump.git`.

3. Rename file `rename_to-data.json` to `data.json`.

4. Open file `data.json` and fill in your RL Garage account `email` and `password` at line `[4]` and `[5]`.

5. Install dependencies:
  
    ### Manually:
    ```
    pip install requests beautifulsoup4
    ```
    OR if that doesn't work:
    ```
    python -m pip install requests beautifulsoup4
    ```
  
    ### From requirements.txt:
    ```
    cd to_repository_location
    pip install -r requirements.txt
    ```

6. Hooray! You are ready to use this tool.

## Using
```
Note: you can always force to stop bumping using CTRL+C combination
```

This tool can be used in three different modes:

#### Regular Mode
Most common mode. Bumping all trades marked with `true` in `data.json`.

To start this mode:
1. Open command prompt and `cd to_repository_location`

2. Run: `python rlautobump.py`

3. Wait untill `Trades updated. Press ENTER to start bumping..` message appears. Then open `data.json` file and mark trades you DO NOT need to bump with `false` (by default they are marked with `true`, so if you want to bump all, skip this step). Save it.

4. Go back to started tool and press ENTER.

#### All in Once mode
This mode updates ALL trades only once. After completing it just stop working. Useful when you need to bump all trades to avoid auto deletion trades after 14 days inactivity.

To start this mode:
1. Open command prompt and `cd to_repository_location`

2. Run: `python rlautobump.py all-once-mode`

3. That's it. Tool will automatically bump all trades.

#### Inverse mode
Inversed version of **Regular** mode. Bumping all trades marked with `false` in `data.json`. Useful when you need to swap between selling/buying trades.

To start this mode:
1. Open command prompt and `cd to_repository_location`

2. Run: `python rlautobump.py inverse-mode`

3. Wait untill `Trades updated. Press ENTER to start bumping..` message appears. Open file `data.json` if you want to change `bump` values for your trades. Save it.

4. Go back to started tool and press ENTER.

## Disclaimer

The author and any contributors associated with this project are not resposible for the consequences that may occur from the use of this tool.

Users of this tool do so entirely at their own risk - abusing this tool could get you permanently banned from Rocket League Garage.

