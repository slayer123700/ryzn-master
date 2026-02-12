import asyncio
import time
import psutil
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app, start_time
from config import config
from Yumeko.decorator.errors import error
from Yumeko.decorator.save import save

OWNER_ID = 7296704435  # Replace with Zaryab's actual Telegram ID

@app.on_message(filters.command("ping", config.COMMAND_PREFIXES))
@error
@save
async def ping_command(_, message: Message):
    """Check the bot's response time and system stats with a shorter loading animation"""

    start = time.time()
    ping_msg = await message.reply_text("Pinging...... ⏳")

    # 4-step loading bar
    loading_bars = [
        "[■□□□]",
        "[■■□□]",
        "[■■■□]",
        "[■■■■]",         
    ]
    for bar in loading_bars:
        await ping_msg.edit_text(f"Pinging... {bar} ⏳")
        await asyncio.sleep(0.3)

    end = time.time()
    ping_time = round((end - start) * 1000, 3)

    uptime = datetime.now() - datetime.fromtimestamp(start_time)
    uptime_str = str(uptime).split('.')[0]

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    response = (
        f"🏓 **PONG!** `{ping_time} ms`\n\n"
        f"⏰ **Uptime:** `{uptime_str}`\n"
        f"🧠 **CPU Usage:** `{cpu_usage}%`\n"
        f"💾 **RAM Usage:** `{ram_usage}%`\n"
        f"🗄️ **Disk Usage:** `{disk_usage}%`\n"
        f"🔖 **Version:** `{config.BOT_VERSION}`\n\n"
        f"👑 **My God:** [Zaryab](tg://user?id={OWNER_ID})"
    )

    await ping_msg.edit_text(response)