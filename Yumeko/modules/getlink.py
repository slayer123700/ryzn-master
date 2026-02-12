from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ChatMemberStatus

from Yumeko import app, config  # Yumeko’s client + config

OWNER_ID = config.OWNER_ID
COMMAND_PREFIXES = getattr(config, "COMMAND_PREFIXES", ["/", "!", ".", "?"])

__module__ = "Get Link"
__help__ = """
🔗 **Get Link**

Owner-only command to fetch a group’s invite link.

**Usage:**
✧ `/getlink <chat_id>` — Get the invite link of a group (bot must be in it).  
"""


@app.on_message(filters.command("getlink", prefixes=COMMAND_PREFIXES))
async def getlink_handler(client, message: Message):
    # ✅ Restrict usage to owner
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ You are not authorized to use this command.")

    # ✅ Must provide chat_id argument
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide the chat ID.\n\nUsage: `/getlink <chat_id>`",
            quote=True,
        )

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid chat ID. Must be a number.", quote=True)

    # ✅ Check bot membership in target chat
    try:
        me = await client.get_me()
        bot_member = await client.get_chat_member(chat_id, me.id)
    except Exception:
        return await message.reply_text(
            "❌ Bot is not present in the specified chat or chat does not exist.",
            quote=True,
        )

    # ✅ Verify bot admin + invite rights
    if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        return await message.reply_text(
            "❌ Bot is not admin in the chat, cannot export invite link.", quote=True
        )
    if not getattr(bot_member.privileges, "can_invite_users", False):
        return await message.reply_text(
            "❌ Bot does not have permission to invite users (cannot export invite link).",
            quote=True,
        )

    # ✅ Export invite link
    try:
        invite_link = await client.export_chat_invite_link(chat_id)
    except ChatAdminRequired:
        return await message.reply_text(
            "❌ Bot lacks permissions to export invite link.", quote=True
        )
    except Exception as e:
        return await message.reply_text(f"❌ Failed to export invite link: {e}", quote=True)

    # ✅ Prepare button
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔗 Join Link", url=invite_link)]]
    )

    # ✅ Send message back
    chat = await client.get_chat(chat_id)

    await message.reply_text(
        f"🔗 **Invite Link Generated**\n\n"
        f"🏠 Chat: {chat.title or 'Unknown'}\n"
        f"🆔 Chat ID: `{chat_id}`\n"
        f"👑 Requested by: {message.from_user.mention}",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )