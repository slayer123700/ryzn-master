import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from Yumeko import app, config  # Yumeko client + config

__module__ = "GitHub"
__help__ = """
🐙 **GitHub Profile Lookup**

Fetches information about a GitHub user.

**Usage:**
✧ `/git <username>` — Get info of a GitHub user.  
✧ `/github <username>` — Same as above.
"""

@app.on_message(filters.command(["github", "git"], prefixes=config.COMMAND_PREFIXES))
async def github_handler(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("❌ Usage: `/git <username>`", quote=True)

    username = message.command[1]
    url = f"https://api.github.com/users/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as request:
            if request.status == 404:
                return await message.reply_text("❌ User not found on GitHub.", quote=True)

            try:
                result = await request.json()
                name = result.get("name") or "N/A"
                profile_url = result.get("html_url") or "N/A"
                bio = result.get("bio") or "N/A"
                company = result.get("company") or "N/A"
                created_at = result.get("created_at") or "N/A"
                blog = result.get("blog") or "N/A"
                location = result.get("location") or "N/A"
                repositories = result.get("public_repos", 0)
                followers = result.get("followers", 0)
                following = result.get("following", 0)

                caption = (
                    f"**👤 GitHub Profile: {name}**\n"
                    f"🆔 **Username:** `{username}`\n"
                    f"📜 **Bio:** `{bio}`\n"
                    f"🔗 **Profile:** {profile_url}\n"
                    f"🏢 **Company:** `{company}`\n"
                    f"📅 **Created On:** `{created_at}`\n"
                    f"📂 **Repositories:** `{repositories}`\n"
                    f"🌐 **Blog:** {blog}\n"
                    f"📍 **Location:** `{location}`\n"
                    f"👥 **Followers:** `{followers}`\n"
                    f"➡️ **Following:** `{following}`"
                )

                return await message.reply_text(
                    caption,
                    disable_web_page_preview=True
                )

            except Exception as e:
                return await message.reply_text(f"❌ Error fetching info: {e}", quote=True)