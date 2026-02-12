from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app
from asyncio import sleep
from pyrogram.errors import PeerIdInvalid
from Yumeko.modules import role_assign

from Yumeko.database.common_chat_db import get_common_chat_count
from Yumeko.database.afk_db import is_user_afk
from Yumeko.database.global_actions_db import is_user_gbanned, is_user_gmuted
from Yumeko.database.user_info_db import get_user_infoo

OWNER_ID = 6125202012
SPECIAL_USER_ID = 7876439267

# Progress bars for loading animation
progress_bars = ["🔴⚪⚪⚪", "🔴🔴⚪⚪", "🔴🔴🔴⚪", "🔴🔴🔴🔴"]

@app.on_message(filters.command("info", prefixes=["/", "!"]))
async def get_user_info(client, message: Message):
    try:
        # Determine target user
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            target = message.command[1]
            if target.isdigit():
                user = await client.get_users(int(target))
            else:
                user = await client.get_users(target)
        else:
            user = message.from_user

        # Loading animation
        progress_msg = await message.reply_text(progress_bars[0])
        for bar in progress_bars[1:]:
            await sleep(0.7)
            await progress_msg.edit_text(bar)

        user_id = user.id
        first_name = user.first_name or "N/A"
        username = f"@{user.username}" if user.username else "No Username"

        try:
            full_user = await app.get_chat(user_id)
            bio = full_user.bio or "No Bio Available"
        except:
            bio = "No Bio Available"

        user_info = await get_user_infoo(user_id)
        custom_bio = user_info.get("custom_bio") if user_info else None
        custom_title = user_info.get("custom_title") if user_info else None

        afk_status = await is_user_afk(user_id)
        gbanned = await is_user_gbanned(user_id)
        gmuted = await is_user_gmuted(user_id)
        common_chats = await get_common_chat_count(user_id)

        # Health calculation
        health = 100
        if username == "No Username":
            health -= 25
        if bio == "No Bio Available":
            health -= 20

        filled_blocks = health // 25
        empty_blocks = 4 - filled_blocks
        health_bar = f"{'🟢' * filled_blocks}{'⚪' * empty_blocks}"
        health_desc = f"New User ({health}%)" if health < 100 else "Healthy User (100%)"

        # Get rank & elite power
        rank, elite_power = role_assign.get_hierarchy(user_id)

        text = (
            "✧･ﾟ: *✧･ﾟ:*\n"
            "👤 **USER INTELLIGENCE REPORT**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🆔 [ `{user_id}` ](tg://user?id={user_id})\n"
            f"📛 {first_name}\n"
            f"🌐 {username}\n"
            f"📶 {'🌙 Currently AFK' if afk_status else '⚡ Active'}\n"
            f"📅 First Seen: Today\n"
            f"👥 Common Chats: {common_chats}\n"
            f"🐾 Special Tag: {custom_title if custom_title else 'None'}\n"
            f"✨ Elite Bio: {custom_bio if custom_bio else bio}\n"
            "▭▭▭▭▭▭▭▭▭▭▭▭▭▭\n"
            "❤️‍🩹 **HEALTH STATUS**\n"
            f"🌱 {health_desc}\n"
            f"{health_bar}\n"
            "▭▭▭▭▭▭▭▭▭▭▭▭▭▭\n"
            "🔰 **Special Power**\n"
            f"🌟 Status: {elite_power}\n"
            f"🎖️ Rank: {rank}\n"
            "▭▭▭▭▭▭▭▭▭▭▭▭▭▭\n"
            "🔒 **SECURITY STATUS**\n"
            f"🚫 GBanned: {'✅' if gbanned else '❌'}\n"
            f"🔇 GMuted: {'✅' if gmuted else '❌'}\n"
            f"🤖 Bot: {'✅' if user.is_bot else '❌'}\n"
            "*:･ﾟ✧*:･ﾟ✧"
        )

        await progress_msg.edit_text(text, disable_web_page_preview=True)

    except PeerIdInvalid:
        await message.reply_text(
            "❌ Unable to find the specified user. Please reply to a message or provide a valid username/ID."
        )
    except Exception as e:
        await message.reply_text(f"❌ An unexpected error occurred: {e}")

__module__ = "Info"

__help__ = """**𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
   
  ✧ `/info` **or** `/info <username/userid>` **or** reply `/info`:  
    𝖲𝗁𝗈𝗐𝗌 𝗍𝖺𝗋𝗀𝖾𝗍 𝗎𝗌𝖾𝗋'𝗌 𝖨𝖣, 𝗉𝗋𝗈𝖿𝗂𝗅𝖾 𝗂𝗇𝖿𝗈, 𝗁𝖾𝖺𝗅𝗍𝗁 𝗌𝗍𝖺𝗍𝗎𝗌, 𝗋𝖺𝗇𝗄, 𝖺𝗇𝖽 𝗌𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝗌𝗍𝖺𝗍𝗎𝗌.
"""