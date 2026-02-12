import os
import json
import shutil
from Yumeko import app
from config import config
from pyrogram.errors import PeerIdInvalid
import asyncio

RESTART_DATA_FILE = "restart_data.json"
SUDOERS_FILE = "sudoers.json"
peer_id = -1003830570193

# ------------------- Restart Data -------------------

def save_restart_data(chat_id, message_id):
    """Save the chat and message ID to a file."""
    with open(RESTART_DATA_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "message_id": message_id}, f)

def load_restart_data():
    """Load the chat and message ID from the file."""
    if os.path.exists(RESTART_DATA_FILE):
        with open(RESTART_DATA_FILE, "r") as f:
            return json.load(f)
    return None

def clear_restart_data():
    """Delete the restart data file."""
    if os.path.exists(RESTART_DATA_FILE):
        os.remove(RESTART_DATA_FILE)

# ------------------- Safe Send Message -------------------

async def safe_send_message(peer_id, text, **kwargs):
    """
    Safely send a message to a chat. Ignores errors if chat not found.
    """
    try:
        peer = await app.get_chat(peer_id)  # Fetches from Telegram if not in session
        await app.send_message(peer.id, text, **kwargs)
    except PeerIdInvalid:
        print(f"[WARN] Peer id invalid: {peer_id}")
    except Exception as e:
        print(f"[WARN] Failed to send message to {peer_id}: {e}")

# ------------------- Restart Message -------------------

def edit_restart_message():
    """Edit the restart message after a successful restart."""
    restart_data = load_restart_data()
    if restart_data:
        async def edit():
            try:
                chat_id = restart_data["chat_id"]
                message_id = restart_data["message_id"]
                await safe_send_message(
                    chat_id,
                    "**𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒!** ✅"
                )
            finally:
                clear_restart_data()
        asyncio.get_event_loop().run_until_complete(edit())

# ------------------- Downloads Cleanup -------------------

def clear_downloads_folder():
    """Remove all files and subdirectories in the downloads folder."""
    downloads_path = "downloads"  # Change this if needed
    if os.path.exists(downloads_path):
        try:
            shutil.rmtree(downloads_path)
            os.makedirs(downloads_path)
            print("Downloads folder cleared successfully.")
        except Exception as e:
            print(f"Failed to clear downloads folder: {e}")

# ------------------- Startup Notification -------------------

def notify_startup():
    """Notify the log channel that the bot has started safely."""
    async def notify():
        await safe_send_message(
            config.LOG_CHANNEL,
            "**𝖡𝗈𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒!** ✅"
        )
    asyncio.get_event_loop().run_until_complete(notify())
