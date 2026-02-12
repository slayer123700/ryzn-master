from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType

from Yumeko import app, config  # Yumeko’s app and config loader

__module__ = "Chat Info"
__help__ = """
📊 **Chat Info**

Get detailed information about the current chat.

**Usage:**
✧ `/chatinfo` — Shows chat title, ID, type, member count, admins count, owner, number of bots, and bot status.
"""

@app.on_message(
    filters.group
    & ~filters.forwarded
    & filters.command("chatinfo", prefixes=config.COMMAND_PREFIXES)
)
async def chatinfo_handler(client, message: Message):
    chat = message.chat

    chat_id = chat.id
    chat_title = chat.title or "Unknown"
    chat_type = chat.type.name if isinstance(chat.type, ChatType) else "Unknown"

    admin_count = "Unknown"
    bot_admin_count = "Unknown"
    owner_mention = "Unknown"
    member_count = "Unknown"
    bot_status = "Unknown"

    # Get admins and owner
    try:
        admins = await client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
        admin_count = len(admins)
        bot_admin_count = sum(1 for admin in admins if admin.user.is_bot)

        for admin in admins:
            if admin.status == ChatMemberStatus.OWNER:
                owner_mention = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"
                break
    except Exception:
        pass

    # Get bot status in chat
    try:
        me = await client.get_me()
        bot_member = await client.get_chat_member(chat_id, me.id)
        bot_status = bot_member.status.name
    except Exception:
        pass

    # Get member count
    try:
        member_count = await client.get_chat_members_count(chat_id)
    except Exception:
        pass

    text = (
        f"📋 **Chat Info** 📋\n\n"
        f"🏷️ **Name:** `{chat_title}`\n"
        f"🆔 **ID:** `{chat_id}`\n"
        f"📂 **Type:** `{chat_type}`\n"
        f"👥 **Members:** `{member_count}`\n"
        f"🔧 **Admins:** `{admin_count}` (Bots: `{bot_admin_count}`)\n"
        f"👑 **Owner:** {owner_mention}\n"
        f"🤖 **Bot Status:** `{bot_status}`"
    )

    await message.reply_text(text, disable_web_page_preview=True)