import io
import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app

@app.on_message(filters.command("weather", prefixes=["/", "!"]))
async def weather(_, message: Message):
    """Fetch weather image for a given city."""
    if len(message.command) < 2:
        return await message.reply_text("`Usage: /weather <city>`")

    city = message.text.split(None, 1)[1]
    url = f"https://wttr.in/{city}.png"

    m = await message.reply_text("`Fetching weather...`")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await m.edit_text(f"`Could not fetch weather for:` {city}")
                data = await resp.read()
                with io.BytesIO(data) as out_file:
                    out_file.name = f"{city}.png"
                    await message.reply_photo(photo=out_file, caption=f"🌤 Weather for **{city}**")
        await m.delete()
    except Exception as e:
        await m.edit_text(f"`Error occurred while fetching weather for:` {city}\n\n`Error:` {e}")

# ---------------- Module Help ----------------
__module__ = "Weather"

__help__ = """*Find Weather*

❍ `/weather <city>` — Fetches the current weather of the city as an image.
❍ `/weather moon` — Gets the current status of the moon.
"""