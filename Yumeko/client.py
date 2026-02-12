from pyrogram import Client
import os

# Get these values from your environment variables or a config file
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7637698136:AAH_49TFYZszJvHfaKGwSvMskkYJyK4oQws")
API_ID = int(os.environ.get("API_ID", "28615030"))
API_HASH = os.environ.get("API_HASH", "4cd09b1bcd45560ee35e8be593f13d83")

pbot = Client(
    "YumekoBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)