import random
import aiohttp
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Yumeko import app


@app.on_message(filters.command(["wall", "wallpaper"], prefixes=["/", "!", ".", "?"]))
async def wallpaper(_, message: Message):
    # Restrict to PM only
    if message.chat.type != ChatType.PRIVATE:
        me = await app.get_me()
        return await message.reply_text(
            "❌ This command only works in **PM**.\n\n👉 [Click Me](tg://user?id={})".format(me.id),
            disable_web_page_preview=True,
        )

    # Extract query text
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a query to search for wallpapers.")

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 Searching for wallpapers...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.safone.me/wall?query={query}") as resp:
                if resp.status != 200:
                    return await m.edit_text(f"❌ Failed to fetch wallpapers (status {resp.status}).")

                data = await resp.json()

        results = data.get("results", [])
        if not results:
            return await m.edit_text(f"❌ No wallpapers found for: `{query}`")

        # Pick a random result from first 4
        ran = random.choice(results[:4])
        img_url = ran.get("imageUrl")

        if not img_url:
            return await m.edit_text("❌ API returned invalid data.")

        await message.reply_photo(
            photo=img_url,
            caption=f"🖼 **Wallpaper for:** `{query}`\n🥀 **Requested by:** {message.from_user.mention}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Open Image", url=img_url)]]
            ),
        )
        await m.delete()

    except Exception as e:
        await m.edit_text(f"⚠️ Error while fetching wallpaper for `{query}`:\n`{e}`")


# ---------------- Module Help ----------------
__module__ = "Wallpapers"
__help__ = """
**Wallpaper Search (PM Only)**

❍ `/wall <query>` — Search wallpapers for a query  
❍ `/wallpaper <query>` — Alias of /wall  

⚠️ This command only works in **private chat (PM)**.
"""