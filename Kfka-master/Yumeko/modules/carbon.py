from pyrogram import filters
from pyrogram.types import Message
import aiohttp
import io
from functools import wraps

from Yumeko import app  # Yumeko’s main client

__module__ = "Carbon"
__help__ = """
❍ /carbon <text> : Generates a carbon image from given text or a replied message.
"""

# Error-catching decorator
def capture_err(func):
    @wraps(func)
    async def wrapper(client, message):
        try:
            return await func(client, message)
        except Exception as e:
            await message.reply_text(f"⚠️ An error occurred: `{e}`")
    return wrapper


# Generate carbon image
async def make_carbon(text: str) -> io.BytesIO:
    urls = [
        "https://carbonara-42.vercel.app/api/cook",   # ✅ Stable clone
        "https://carbonara.vercel.app/api/cook",      # Old API (fallback)
    ]

    for url in urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"code": text}) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.read()
                    carbon = io.BytesIO(data)
                    carbon.name = "carbon.png"  # required for send_photo
                    return carbon
        except Exception:
            continue

    raise Exception("All Carbon APIs failed. Please try again later.")


# Command handler
@app.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message: Message):
    # Get text input
    if message.reply_to_message and message.reply_to_message.text:
        txt = message.reply_to_message.text
    else:
        try:
            txt = message.text.split(None, 1)[1]
        except IndexError:
            return await message.reply_text(
                "⚠️ Reply to a message or provide some text to generate carbon."
            )

    # Notify user
    m = await message.reply_text("⚡ Generating carbon image...")

    # Generate carbon
    carbon = await make_carbon(txt)

    # Upload result
    await m.edit_text("📤 Uploading generated carbon...")
    await app.send_photo(
        chat_id=message.chat.id,
        photo=carbon,
        caption=f"» Requested by: {message.from_user.mention}"
    )

    await m.delete()
    carbon.close()