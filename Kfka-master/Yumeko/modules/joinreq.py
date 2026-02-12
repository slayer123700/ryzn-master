import json
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, ChatJoinRequest, InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from Yumeko import app, JOIN_UPDATE_GROUP
from Yumeko.decorator.botadmin import user_has_role

NOTIFY_FILE = "join_notify.json"

# Load/Save notification settings for chats
def load_notify_settings():
    if not os.path.exists(NOTIFY_FILE):
        with open(NOTIFY_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(NOTIFY_FILE, "r") as f:
        return json.load(f)

def save_notify_settings(data):
    with open(NOTIFY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Check if join notifications enabled for a chat
def is_notify_enabled(chat_id):
    data = load_notify_settings()
    return str(chat_id) in data and data[str(chat_id)] is True

# Command to enable/disable join request notifications
@app.on_message(filters.command("request") & filters.group)
async def toggle_join_notifications(client: Client, message):
    if not message.from_user:
        return

    # Check if the sender is admin with invite rights
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in {CMS.OWNER, CMS.ADMINISTRATOR} or not member.privileges.can_invite_users:
            await message.reply("❌ You must be an admin with permission to add users to use this command.")
            return
    except Exception:
        await message.reply("❌ Unable to verify your admin status. Make sure I’m an admin too.")
        return

    # Check if the bot has invite rights
    try:
        bot_member = await client.get_chat_member(message.chat.id, client.me.id)
        if bot_member.status not in {CMS.OWNER, CMS.ADMINISTRATOR} or not bot_member.privileges.can_invite_users:
            await message.reply("❌ I need admin rights with permission to add users.")
            return
    except Exception:
        await message.reply("❌ Unable to verify my admin rights.")
        return

    if len(message.command) < 2:
        await message.reply(
            "Usage:\n"
            "/request enable - Enable join request notifications\n"
            "/request disable - Disable join request notifications"
        )
        return

    action = message.command[1].lower()
    settings = load_notify_settings()
    chat_id_str = str(message.chat.id)

    if action == "enable":
        settings[chat_id_str] = True
        save_notify_settings(settings)
        await message.reply("🟢 Join request notifications enabled for this chat.")
    elif action == "disable":
        settings[chat_id_str] = False
        save_notify_settings(settings)
        await message.reply("🚨 Join request notifications disabled for this chat.")
    else:
        await message.reply("Invalid option! Use enable or disable.")

# Join request handler
@app.on_chat_join_request(group=JOIN_UPDATE_GROUP)
async def join_request_handler(client: Client, join_request: ChatJoinRequest):
    chat_id = join_request.chat.id
    if not is_notify_enabled(chat_id):
        return  # Notifications disabled

    user = join_request.from_user
    txt = (
        "🚨 Join Request Detected 🚪\n\n"
        "👤 User Details:\n"
        f"• ⚜️ Name: {user.full_name}\n"
        f"• 🆔 ID: {user.id}\n"
        f"• 🔗 Profile: {user.mention}\n"
        f"• 🚨 Scam Flag: {'✅ Yes' if user.is_scam else '❌ No'}\n"
    )

    if user.username:
        txt += f"Username: @{user.username}\n"

    kb = [
        [
            ikb("🟢 Accept", f"accept_joinreq_{user.id}"),
            ikb("🔴 Decline", f"decline_joinreq_{user.id}")
        ]
    ]
    await client.send_message(chat_id, txt, reply_markup=ikm(kb))

# Callback query handler
@app.on_callback_query(filters.regex(r"^(accept|decline)_joinreq_\d+$"))
async def joinreq_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    # Check permissions
    is_bot_admin = user_has_role(user_id, "Botadmin")
    is_chat_admin = False
    try:
        member = await query.message.chat.get_member(user_id)
        is_chat_admin = (member.status in {CMS.OWNER, CMS.ADMINISTRATOR} and member.privileges.can_invite_users)
    except Exception:
        pass

    if not (is_bot_admin or is_chat_admin):
        await query.answer("❌ You are not authorized to do this!", show_alert=True)
        return

    action, _, target_user_id = query.data.partition("_joinreq_")
    target_user_id = int(target_user_id)

    try:
        target_user = await client.get_users(target_user_id)
    except Exception:
        target_user = None

    try:
        if action == "accept":
            await client.approve_chat_join_request(chat_id, target_user_id)
            await query.answer(f"Accepted join request of {target_user.mention if target_user else target_user_id}")
            await query.edit_message_text(f"{query.from_user.mention} accepted join request of {target_user.mention if target_user else target_user_id}")
        else:
            await client.decline_chat_join_request(chat_id, target_user_id)
            await query.answer(f"Declined join request of {target_user.mention if target_user else target_user_id}")
            await query.edit_message_text(f"{query.from_user.mention} declined join request of {target_user.mention if target_user else target_user_id}")
    except UserNotParticipant:
        await query.answer("Join request no longer available or cancelled.", show_alert=True)
        await query.edit_message_text(f"Join request for {target_user.mention if target_user else target_user_id} no longer available.")
    except PeerIdInvalid:
        await query.answer("User is deleted or unavailable.", show_alert=True)
        await query.edit_message_text(f"User (ID: {target_user_id}) no longer available.")
    except ChatAdminRequired:
        await query.answer("I need admin rights to manage join requests.", show_alert=True)
        await query.edit_message_text("I need admin rights to manage join requests.")
    except Exception as e:
        await query.answer(f"Error: {str(e)[:20]}...", show_alert=True)
        await query.edit_message_text("Error while processing join request.")

module = "𝖩𝗈𝗂𝗇 𝖱𝖾𝗊𝗎𝖾𝗌𝗍"

help = """𝖩𝗈𝗂𝗇 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖬𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍:

- 𝖮𝗏𝖾𝗋𝗏𝗂𝖾𝗐:
  𝖳𝗁𝗂𝗌 𝗆𝗈𝖽𝗎𝗅𝖾 𝗁𝖾𝗅𝗉𝗌 𝖺𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝗍𝗈𝗋𝗌 𝗆𝖺𝗇𝖺𝗀𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍𝗌 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗁𝖾𝗋𝖾 𝗍𝗁𝖾 𝖺𝗉𝗉𝗋𝗈𝗏𝖺𝗅 𝗌𝗒𝗌𝗍𝖾𝗆 𝗂𝗌 𝖾𝗇𝖺𝖻𝗅𝖾𝖽.

- 𝖤𝗇𝖺𝖻𝗅𝖾/𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:
  ✧ /request enable — 𝖤𝗇𝖺𝖻𝗅𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗇𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇𝗌 𝗂𝗇 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉.
  ✧ /request disable — 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗇𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇𝗌.

- 𝖥𝗎𝗇𝖼𝗍𝗂𝗈𝗇𝖺𝗅𝗂𝗍𝗒:
  ✧ 𝖭𝗈𝗍𝗂𝖿𝗂𝖾𝗌 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉 𝗐𝗁𝖾𝗇 𝖺 𝗇𝖾𝗐 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗌 𝗋𝖾𝖼𝖾𝗂𝗏𝖾𝖽.
    ✧ 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋'𝗌 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇, 𝗌𝗎𝖼𝗁 𝖺𝗌:
      - 𝖭𝖺𝗆𝖾, 𝗆𝖾𝗇𝗍𝗂𝗈𝗇, 𝖺𝗇𝖽 𝖨𝖣.
      - 𝖲𝖼𝖺𝗆 𝗌𝗍𝖺𝗍𝗎𝗌.
      - 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾 (𝗂𝖿 𝖺𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾).
    ✧ 𝖯𝗋𝗈𝗏𝗂𝖽𝖾𝗌 𝗂𝗇𝗅𝗂𝗇𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝗍𝗈 𝖾𝗂𝗍𝗁𝖾𝗋 𝖺𝖼𝖼𝖾𝗉𝗍 𝗈𝗋 𝖽𝖾𝖼𝗅𝗂𝗇𝖾 𝗍𝗁𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.

- 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖺𝗇𝖽 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌:

  ✧ 𝖭𝖾𝗐 𝖩𝗈𝗂𝗇 𝖱𝖾𝗊𝗎𝖾𝗌𝗍:
    - 𝖶𝗁𝖾𝗇 𝖺 𝗇𝖾𝗐 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗌 𝖽𝖾𝗍𝖾𝖼𝗍𝖾𝖽, 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗌𝖾𝗇𝖽𝗌 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗐𝗂𝗍𝗁 𝗎𝗌𝖾𝗋 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝖺𝗇𝖽 𝗈𝗉𝗍𝗂𝗈𝗇𝗌 𝗍𝗈 𝖾𝗂𝗍𝗁𝖾𝗋 𝖺𝖼𝖼𝖾𝗉𝗍 𝗈𝗋 𝖽𝖾𝖼𝗅𝗂𝗇𝖾 𝗍𝗁𝖾 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.
      - 𝖳𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗂𝗇𝖼𝗅𝗎𝖽𝖾𝗌 𝗍𝗁𝖾 𝖿𝗈𝗅𝗅𝗈𝗐𝗂𝗇𝗀 𝖻𝗎𝗍𝗍𝗈𝗇𝗌:
        - 𝖠𝖼𝖼𝖾𝗉𝗍: 𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋'𝗌 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.
        - 𝖣𝖾𝖼𝗅𝗂𝗇𝖾: 𝖣𝖾𝖼𝗅𝗂𝗇𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋'𝗌 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.

  ✧ 𝖠𝗉𝗉𝗋𝗈𝗏𝖺𝗅/𝖣𝖾𝖼𝗅𝗂𝗇𝖾:
    - 𝖢𝗅𝗂𝖼𝗄𝗂𝗇𝗀 𝗈𝗇 𝗍𝗁𝖾 "𝖠𝖼𝖼𝖾𝗉𝗍" 𝖻𝗎𝗍𝗍𝗈𝗇 𝖺𝗉𝗉𝗋𝗈𝗏𝖾𝗌 𝗍𝗁𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.
    - 𝖢𝗅𝗂𝖼𝗄𝗂𝗇𝗀 𝗈𝗇 𝗍𝗁𝖾 "𝖣𝖾𝖼𝗅𝗂𝗇𝖾" 𝖻𝗎𝗍𝗍𝗈𝗇 𝗋𝖾𝗃𝖾𝖼𝗍𝗌 𝗍𝗁𝖾 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.
    - 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝗍𝗈𝗋𝗌, 𝗈𝗐𝗇𝖾𝗋𝗌, 𝗈𝗋 𝖻𝗈𝗍 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗍𝖺𝗄𝖾 𝗍𝗁𝖾𝗌𝖾 𝖺𝖼𝗍𝗂𝗈𝗇𝗌.
    - 𝖭𝗈𝗇-𝖺𝖽𝗆𝗂𝗇𝗌 𝖺𝗍𝗍𝖾𝗆𝗉𝗍𝗂𝗇𝗀 𝗍𝗈 𝗂𝗇𝗍𝖾𝗋𝖺𝖼𝗍 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝗐𝗂𝗅𝗅 𝗋𝖾𝖼𝖾𝗂𝗏𝖾 𝖺𝗇 𝖺𝗅𝖾𝗋𝗍.
"""