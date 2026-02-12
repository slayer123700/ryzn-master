import os
import json
import shutil
import asyncio
from Yumeko import app, log
from config import config
from pyrogram.errors import PeerIdInvalid

RESTART_DATA_FILE = "restart_data.json"

# --- Restart message handling ---
def save_restart_data(chat_id, message_id):
    """Save chat and message ID for editing after restart."""
    with open(RESTART_DATA_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "message_id": message_id}, f)

def load_restart_data():
    if os.path.exists(RESTART_DATA_FILE):
        with open(RESTART_DATA_FILE, "r") as f:
            return json.load(f)
    return None

def clear_restart_data():
    if os.path.exists(RESTART_DATA_FILE):
        os.remove(RESTART_DATA_FILE)

# --- Safe message sending ---
async def safe_send_message(peer, text, **kwargs):
    """
    Send a message safely.
    Peer can be username (preferred) or numeric ID.
    """
    try:
        await app.send_message(peer, text, **kwargs)
    except PeerIdInvalid:
        log.warning(f"[on_start] Invalid peer: {peer} (bot may not have access)")
    except Exception as e:
        log.warning(f"[on_start] Failed to send message to {peer}: {e}")

def edit_restart_message():
    """Edit the previous restart message if it exists."""
    restart_data = load_restart_data()
    if restart_data:
        async def edit():
            try:
                await app.edit_message_text(
                    chat_id=restart_data["chat_id"],
                    message_id=restart_data["message_id"],
                    text="**Bot restarted successfully! ✅**"
                )
            except PeerIdInvalid:
                log.warning(f"[on_start] Cannot edit message, invalid peer ID: {restart_data['chat_id']}")
            except Exception as e:
                log.warning(f"[on_start] Failed to edit restart message: {e}")
            finally:
                clear_restart_data()
        asyncio.get_event_loop().run_until_complete(edit())

# --- Downloads folder cleanup ---
def clear_downloads_folder():
    downloads_path = config.DOWNLOAD_LOCATION
    if os.path.exists(downloads_path):
        try:
            shutil.rmtree(downloads_path)
            os.makedirs(downloads_path)
            log.info("[on_start] Downloads folder cleared successfully.")
        except Exception as e:
            log.warning(f"[on_start] Failed to clear downloads folder: {e}")

# --- Startup notification ---
def notify_startup():
    """
    Notify log and error channels safely.
    Only works for channels/groups the bot is already in.
    """
    async def notify():
        if config.LOG_CHANNEL:
            await safe_send_message(config.LOG_CHANNEL, "**Bot has started successfully! ✅**")
        if config.ERROR_LOG_CHANNEL and config.ERROR_LOG_CHANNEL != config.LOG_CHANNEL:
            await safe_send_message(config.ERROR_LOG_CHANNEL, "**Bot started. Ready to log errors. ✅**")
    asyncio.get_event_loop().run_until_complete(notify())
