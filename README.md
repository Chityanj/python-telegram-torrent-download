# Torrent Bot with Download and Zip Functionality

This Telegram bot allows you to download torrents using magnet links and provides additional functionality to zip and send downloaded files.

## Setup

1. Clone this repository to your local machine.
2. Install the required Python libraries by running: `pip install -r requirements.txt`
3. Create a new bot on Telegram and obtain your Bot API Token.
4. Replace `'YOUR_BOT_TOKEN_HERE'` in the code with your actual Telegram Bot API token.

## Usage

1. Start the bot by running the script: `python bot.py`
2. Send the `/start` command to the bot to receive instructions.
3. To download a torrent, use the `/download <magnet link>` command.
4. To download and zip a torrent, use the `/downloadzip <magnet link>` command.

## Features

- The bot provides live updates on the progress of ongoing downloads.
- The `/cancel <magnet link>` command can be used to cancel an ongoing download.
- The `/downloadzip` command downloads a torrent, zips the file, sends it, and removes the original and zipped files.

## Notes

- The bot uses the `libtorrent` library to handle torrent downloads.
- Active downloads are tracked using the `active_downloads` dictionary.
- The `params` dictionary controls the download parameters.
