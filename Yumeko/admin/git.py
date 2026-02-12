import os
import subprocess
import sys
from pyrogram import filters
from Yumeko import app
from config import config 
from Yumeko.helper.on_start import save_restart_data
from Yumeko.decorator.errors import error
from Yumeko.decorator.save import save

@app.on_message(filters.command("update", prefixes=config.COMMAND_PREFIXES) & filters.user(config.OWNER_ID))
@error
@save
async def git_pull_command(client, message):
    try:
        # Stash local changes to prevent merge conflicts
        subprocess.run(["git", "stash"], check=True)

        result = subprocess.run(
            ["git", "pull", config.GIT_URL_WITH_TOKEN , "main"],
            capture_output=True, text=True, check=True
        )
        if "Already up to date" in result.stdout:
            await message.reply("Rᴇᴘᴏ ɪs ᴀʟʀᴇᴀᴅʏ ᴜᴘ ᴛᴏ ᴅᴀᴛᴇ.")
        elif result.returncode == 0:
            restart_message = await message.reply("Gɪᴛ ᴘᴜʟʟ sᴜᴄᴄᴇssғᴜʟ. Bᴏᴛ ᴜᴘᴅᴀᴛᴇᴅ.\n\nRᴇsᴛᴀʀᴛɪɴɢ...")
            save_restart_data(restart_message.chat.id, restart_message.id)
            await restart_bot()
        else:
            await message.reply("Gɪᴛ ᴘᴜʟʟ ғᴀɪʟᴇᴅ. Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟᴏɢs.")
    except subprocess.CalledProcessError as e:
        await message.reply(f"Gɪᴛ ᴘᴜʟʟ ғᴀɪʟᴇᴅ ᴡɪᴛʜ ᴇʀʀᴏʀ: {e.stderr}")

async def restart_bot():
    args = [sys.executable, "-m", "Yumeko"]  # Adjust this line as needed
    os.execle(sys.executable, *args, os.environ)
    sys.exit()

@app.on_message(filters.command("restart") & filters.user(config.OWNER_ID))
@error
@save
async def restart_command(client, message):
    try:
        restart_message = await message.reply("**𝐊ᴀғᴋᴀ 𝐇ᴏɴᴋᴀɪ ɪꜱ ʙᴇɪɴɢ ʀᴇꜱᴛᴀʀᴛᴇᴅ !!**")
        save_restart_data(restart_message.chat.id, restart_message.id)
        os.execvp(sys.executable, [sys.executable, "-m", "Yumeko"])
    except Exception as e:
        await message.reply(f"Rᴇsᴛᴀʀᴛ ғᴀɪʟᴇᴅ ᴡɪᴛʜ ᴇʀʀᴏʀ: {str(e)}")
        