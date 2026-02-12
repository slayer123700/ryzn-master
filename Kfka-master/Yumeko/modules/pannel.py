__module__ = "Panel"

__help__ = """
**𝖯𝖺𝗇𝖾𝗅 (𝗢𝗐𝗇𝖾𝗋 𝗢𝗇𝗅𝗒):**

✧ `/panel` : 𝖮𝗉𝖾𝗇 𝗍𝗁𝖾 𝗈𝗐𝗇𝖾𝗋'𝗌 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖺𝗇𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅 𝗉𝖺𝗇𝖾𝗅 𝖶𝗂𝗍𝗁 𝖺𝗅𝗅 𝗏𝗂𝗍𝖺𝗅 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.

**𝖴𝗌𝖺𝗀𝖾:**

✧ `/panel` : 𝖲𝗁𝗈𝗐𝗌 𝖺 𝗅𝗂𝗌𝗍 𝗈𝖿 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝗎𝗌𝖾𝖿𝗎𝗅 𝗋𝗈𝗅𝖾𝗌 𝗅𝗂𝗄𝖾 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍, 𝗆𝗈𝗉, 𝗌𝗎𝗉𝗉𝗈𝗋𝗍, 𝖺𝗇𝖽 𝗈𝗐𝗇𝖾𝗋 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.

✧ 𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝘀:
   •  `/panel`

"""
PANEL_TEXT = """
📜 **Available Commands:**
• 🚪 /leave <chat_id> — Leave a group
• 🔇 /gmute <user_id> — Globally mute a user
• 🔊 /ungmute <user_id> — Remove global mute
• ⛔ /gban <user_id> — Globally ban a user
• ♻️ /ungban <user_id> — Remove global ban
• 🔗 /getlink <chat_id> — Get group invite link
• 📋 /gmuted — List all globally muted users
• 📋 /gbanned — List all globally banned users
• 📢 /ycast <message> — Broadcast a message

🛠 **Admin Control:**
• 📌 /assign — Promote bot to admin in chat
• 📍 /unassign — Remove bot's admin rights
• 👥 /staffs — Check list of current staff members

🚫 **Block Control:**
• 🚷 /block <user_id> — Block a user from bot usage
• ♻️ /unblock <user_id> — Unblock a user
• 📜 /blocked — List all blocked users
• 🚷 /blockchat <chat_id> — Block a chat from using the bot
• ♻️ /unblockchat <chat_id> — Unblock a chat
• 📜 /blockedchat — List all blocked chats

⚙️ **System Tools:**
• 📊 /stats — Show bot statistics
• ⚡ /speedtest — Run internet speed test
• ✉️ /send <chat_id> <text> — Send a message to a chat
• 🐍 /eval <code> — Run Python code
• 💾 /backup — Backup bot database/files
• 📥 /restore — Restore from backup
• 🔧 /maintenance enable|disable — Toggle maintenance mode
• 🔄 /restart — Restart the bot
"""

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from Yumeko import app  # Adjust import based on your project structure

@app.on_message(filters.command("panel", prefixes=["/", "!"]))
async def panel_handler(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ Only the bot owner can access this command.")
        return

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗑 Delete", callback_data="panel_delete")]
        ]
    )
    await message.reply_text(PANEL_TEXT, reply_markup=keyboard)

@app.on_callback_query(filters.user(OWNER_ID) & filters.regex("^panel_delete$"))
async def panel_delete_handler(client, cq: CallbackQuery):
    try:
        await cq.message.delete()
        await cq.answer()  # no notification on delete
    except:
        await cq.answer("⚠️ Can't delete message!", show_alert=True)