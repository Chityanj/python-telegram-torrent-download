import telebot 
import libtorrent as lt
import time
import traceback
import zipfile
import os

BOT_TOKEN = 'TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)
params = {
    'save_path': '.',  
    'storage_mode': lt.storage_mode_t(2),  
}

active_downloads = {}

def format_size(size):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(suffixes) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {suffixes[index]}"

def print_progress_bar(progress):
    bar_length = 40
    block = int(round(bar_length * progress))
    progress_bar = "[" + "=" * block + " " * (bar_length - block) + "]"
    return progress_bar

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'To download, type /download <magnet link> \nTo cancel, type /cancel <magnet link> \nTo download and zip, type /downloadzip <magnet link>')

@bot.message_handler(commands=['download'])
def download_message(message):
    command = message.text.split(' ', 1)
    if len(command) < 2:
        bot.send_message(message.chat.id, 'Usage: /download <magnet link>')
        return
    
    magnet_link = command[1]
    try:
        ses = lt.session()
        handle = lt.add_magnet_uri(ses, magnet_link, params)
        torrent_name = handle.name()
        active_downloads[magnet_link] = handle
        message = bot.send_message(message.chat.id, f"Downloading: {torrent_name}")
        
        while not handle.is_seed():
            s = handle.status()

            download_speed = format_size(s.download_rate)
            seeders = s.num_seeds
            leechers = s.num_peers - seeders
            progress = s.progress
            progress_bar = print_progress_bar(progress)

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"Name: {torrent_name}\n"
                     f"Progress: {progress_bar} {progress*100:.2f}%\n"
                     f"Download Speed: {download_speed}/s\n"
                     f"Leechers: {leechers} | Seeders: {seeders}"
            )
            time.sleep(2)  # Adjust the interval as needed

        bot.send_message(message.chat.id, "Download complete!")
        del active_downloads[magnet_link]  # Remove the download from active_downloads

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
        traceback.print_exc()

@bot.message_handler(commands=['cancel'])
def cancel_message(message):
    command = message.text.split(' ', 1)
    if len(command) < 2:
        bot.send_message(message.chat.id, 'Usage: /cancel <magnet link>')
        return
    
    magnet_link = command[1]
    if magnet_link in active_downloads:
        try:
            handle = active_downloads[magnet_link]
            handle.pause()
            del active_downloads[magnet_link]
            bot.send_message(message.chat.id, "Download cancelled!")
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred while cancelling: {str(e)}")
            traceback.print_exc()
    else:
        bot.send_message(message.chat.id, "No active download found with that magnet link.")

@bot.message_handler(commands=['downloadzip'])
def download_zip_message(message):
    command = message.text.split(' ', 1)
    if len(command) < 2:
        bot.send_message(message.chat.id, 'Usage: /downloadzip <magnet link>')
        return
    
    magnet_link = command[1]
    try:
        ses = lt.session()
        handle = lt.add_magnet_uri(ses, magnet_link, params)
        torrent_name = handle.name()
        active_downloads[magnet_link] = handle
        message = bot.send_message(message.chat.id, f"Downloading: {torrent_name}")

        while not handle.is_seed():
            s = handle.status()

            download_speed = format_size(s.download_rate)
            seeders = s.num_seeds
            leechers = s.num_peers - seeders
            progress = s.progress
            progress_bar = print_progress_bar(progress)

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"Name: {torrent_name}\n"
                    f"Progress: {progress_bar} {progress*100:.2f}%\n"
                    f"Download Speed: {download_speed}/s\n"
                    f"Leechers: {leechers} | Seeders: {seeders}"
            )
            time.sleep(2)  # Adjust the interval as needed

        # Download complete
        del active_downloads[magnet_link]
        bot.send_message(message.chat.id, "Download complete!")

        # Zip the downloaded file and remove the original file
        file_name = os.path.join(params['save_path'], torrent_name)
        zip_file_name = file_name + '.zip'
        
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_name, os.path.basename(file_name))
        
        os.remove(file_name)

        # Send the zipped file
        with open(zip_file_name, 'rb') as zip_file:
            bot.send_document(message.chat.id, zip_file)

        os.remove(zip_file_name)

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
        traceback.print_exc()


bot.polling()
