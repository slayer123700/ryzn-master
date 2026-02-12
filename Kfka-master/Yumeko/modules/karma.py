from Yumeko.database import karma_db
from pyrogram import Client, filters
from pyrogram.types import Message
from Yumeko import app
import config 

@app.on_message(filters.command("karma", prefixes=config.config.COMMAND_PREFIXES) & filters.group)
async def show_karma(client: Client, message: Message):
    """Show the karma points of a user."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Get the user's karma points
    user_karma = await karma_db.get_karma(user_id, chat_id)
    await message.reply_text(f"Your current karma points is  **{user_karma}** ")

@app.on_message(filters.command("topkarma", prefixes=config.config.COMMAND_PREFIXES) & filters.group)
async def show_top_karma(client: Client, message: Message):
    """Show the top users with the highest karma in the group."""
    chat_id = message.chat.id

    # Get the top karma users
    top_users = await karma_db.top_karma(chat_id)
    if not top_users:
        await message.reply_text("No karma data available for this group.")
        return

    leaderboard = "\n".join(
        [f"**{i + 1}.** {user['user_name']} ({user['user_id']}) -: **{user['karma']}** Points" for i, user in enumerate(top_users)]
    )
    await message.reply_text(f"🏆 **Top Karma Users in this Group**\n\n{leaderboard}")

@app.on_message(filters.regex(
        r"(?i)^(\+|\+\+|\+1|thx|tnx|ty|tq|thank you|thanx|thanks|pro|cool|good|agree|makasih|👍|\+\+ .+)$"
    ) & filters.group & filters.reply)
async def increase_karma_handler(client: Client, message: Message):
    target_user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    name = message.reply_to_message.from_user.first_name

    # Increase the target user's karma points
    await karma_db.increase_karma(target_user_id, name , chat_id)
    await message.reply_text(f"Increased karma for **{message.reply_to_message.from_user.mention}**")

@app.on_message(filters.regex(r"(?i)^(-|--|-1|not cool|disagree|worst|bad|👎|-- .+)$") & filters.group & filters.reply)
async def decrease_karma_handler(client: Client, message: Message):

    target_user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    name = message.reply_to_message.from_user.first_name

    # Decrease the target user's karma points
    await karma_db.decrease_karma(target_user_id, name , chat_id)
    await message.reply_text(f"Decreased karma for **{message.reply_to_message.from_user.mention}**")


__module__ = "𝖪𝖺𝗋𝗆𝖺"

__help__ = """**🏆 𝖪𝖺𝗋𝗆𝖺 𝖲𝗒𝗌𝗍𝖾𝗆:**

- **𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
 ✧ `/karma` — 𝖲𝗁𝗈𝗐𝗌 𝗒𝗈𝗎𝗋 𝖼𝗎𝗋𝗋𝖾𝗇𝗍 𝗄𝖺𝗋𝗆𝖺 𝗉𝗈𝗂𝗇𝗍𝗌.
 ✧ `/topkarma` — 𝖲𝗁𝗈𝗐𝗌 𝗍𝗁𝖾 𝗍𝗈𝗉 𝗎𝗌𝖾𝗋𝗌 𝗐𝗂𝗍𝗁 𝗁𝗂𝗀𝗁𝖾𝗌𝗍 𝗄𝖺𝗋𝗆𝖺 𝗂𝗇 𝗍𝗁𝗂𝗌 𝗀𝗋𝗈𝗎𝗉.

- **𝖠𝗎𝗍𝗈-𝖠𝖼𝗍𝗂𝗈𝗇𝗌:**
   • Reply with **+**, **++**, **+1**, "thanks", 👍 etc. → 𝖨𝗇𝖼𝗋𝖾𝖺𝗌𝖾 𝗍𝗁𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗎𝗌𝖾𝗋’𝗌 𝗄𝖺𝗋𝗆𝖺.
   • Reply with **-**, **--**, **-1**, "bad", 👎 etc. → 𝖣𝖾𝖼𝗋𝖾𝖺𝗌𝖾 𝗍𝗁𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗎𝗌𝖾𝗋’𝗌 𝗄𝖺𝗋𝗆𝖺.

- **𝖴𝗌𝖺𝗀𝖾:**
   1. Type `/karma` to check your points.
   2. Use `/topkarma` to view the group leaderboard.
   3. React positively/negatively in replies to adjust karma.
"""