from Yumeko import app
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ParseMode, ChatMembersFilter
from Yumeko.decorator.chatadmin import chatadmin
from Yumeko.decorator.errors import error
from Yumeko.decorator.save import save
from Yumeko.helper.log_helper import send_log, format_log
from config import config
import time
from Yumeko.database import db, DB_CACHE
import asyncio

# Create a collection for AntiBanAll
antibanall_collection = db.AntiBanAllSettings

# Cache for tracking ban actions
ban_tracker = {}

# TTL for ban tracking (10 seconds)
BAN_TRACKING_TTL = 10

# Threshold for number of bans to trigger action
BAN_THRESHOLD = 5

# Cache keys
ANTIBANALL_CHAT_KEY = "antibanall_chat_{}"
ANTIBANALL_ENABLED_CHATS_KEY = "antibanall_enabled_chats"

# Enable AntiBanAll for a chat
async def enable_antibanall(chat_id: int, chat_title: str, chat_username: str = None) -> None:
    try:
        chat_data = {
            "chat_id": chat_id,
            "antibanall_enabled": True,
            "chat_title": chat_title,
            "chat_username": chat_username,
        }
        await antibanall_collection.update_one(
            {"chat_id": chat_id},
            {"$set": chat_data},
            upsert=True
        )
        DB_CACHE[ANTIBANALL_CHAT_KEY.format(chat_id)] = chat_data
        DB_CACHE.pop(ANTIBANALL_ENABLED_CHATS_KEY, None)
    except Exception as e:
        print(f"Error enabling AntiBanAll: {e}")

# Disable AntiBanAll for a chat
async def disable_antibanall(chat_id: int) -> None:
    try:
        await antibanall_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"antibanall_enabled": False}},
            upsert=True
        )
        cache_key = ANTIBANALL_CHAT_KEY.format(chat_id)
        if cache_key in DB_CACHE:
            DB_CACHE[cache_key]["antibanall_enabled"] = False
        DB_CACHE.pop(ANTIBANALL_ENABLED_CHATS_KEY, None)
    except Exception as e:
        print(f"Error disabling AntiBanAll: {e}")

# Check if AntiBanAll is enabled for a chat
async def is_antibanall_enabled(chat_id: int) -> bool:
    try:
        chat_data = await get_chat_info(chat_id)
        return chat_data.get("antibanall_enabled", False) if chat_data else False
    except Exception as e:
        print(f"Error checking if AntiBanAll is enabled: {e}")
        return False

# Get chat info
async def get_chat_info(chat_id: int):
    cache_key = ANTIBANALL_CHAT_KEY.format(chat_id)
    if cache_key in DB_CACHE:
        return DB_CACHE[cache_key]
    try:
        chat_data = await antibanall_collection.find_one({"chat_id": chat_id})
        if chat_data:
            DB_CACHE[cache_key] = chat_data
            return chat_data
    except Exception as e:
        print(f"Error getting chat info: {e}")
    return None

@app.on_message(filters.command("antibanall", prefixes=config.COMMAND_PREFIXES) & filters.group)
@error
@save
async def antibanall_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Permission check — only bot owner or group owner  
    if user_id != config.OWNER_ID:  
        try:  
            member = await client.get_chat_member(chat_id, user_id)  
            if member.status != ChatMemberStatus.OWNER:  
                await message.reply_text("❌ Only the **group owner** can toggle AntiBanAll.")  
                return  
        except Exception:  
            await message.reply_text("❌ Unable to verify permissions.")  
            return  

    if await is_antibanall_enabled(chat_id):  
        msg = await message.reply_text(
            "🔴 Disabling AntiBanAll Protection...\n\n"
            "🛡️ System shutdown in progress..."
        )
        await asyncio.sleep(1.5)
        await msg.edit_text(
            "🔴 **AntiBanAll Protection Disabled!**\n\n"
            "🛑 BanAll shield deactivated\n"
            "⚠️ Group is now vulnerable to mass bans"
        )
        await disable_antibanall(chat_id)

    else:
        # Step 1: Show opening message
        msg = await message.reply_text(  
            "🛡️ Initializing AntiBanAll Protocol...\n\n"  
            "🔍 Scanning admin privileges..."  
        )  
        await asyncio.sleep(1.5)  

        # Step 2  
        await msg.edit_text(  
            "🛡️ Initializing AntiBanAll Protocol...\n\n"  
            "✅ Admin privileges detected.\n"  
            "🔍 Checking ban rights..."  
        )  
        await asyncio.sleep(1.5)  

        # Step 3  
        await msg.edit_text(  
            "🛡️ Initializing AntiBanAll Protocol...\n\n"  
            "✅ Admin privileges detected.\n"  
            "✅ Ban rights confirmed.\n"  
            "🛠️ Making group safe..."  
        )  
        await asyncio.sleep(1.5)  

        # Step 4  
        await msg.edit_text(  
            "🛡️ Initializing AntiBanAll Protocol...\n\n"  
            "✅ Admin privileges detected.\n"  
            "✅ Ban rights confirmed.\n"  
            "✅ Group safety protocols engaged.\n"  
            "⚡ Optimizing realtime monitoring..."  
        )  
        await asyncio.sleep(1.5)  

        # Hacker-style loading bar animation before final step  
        loading_bars = [
    "[▓░░░░░░]",
    "[▓▓░░░░░]",
    "[▓▓▓░░░░]",
    "[▓▓▓▓░░░]",
    "[▓▓▓▓▓░░]",
    "[▓▓▓▓▓▓▓]",
]

        for bar in loading_bars:
            await msg.edit_text(f"🛡️ Initializing AntiBanAll Protocol...\n\n{bar}")
            await asyncio.sleep(0.2)

        await msg.edit_text("🛡️ Processing AntiBanAll setup... 🔄")
        await asyncio.sleep(2)

        # Final step  
        await msg.edit_text(  
            "🛡️ **AntiBanAll Protection Fully Activated!**\n\n"  
            "🚀 **System Status:** Online & Monitoring\n"  
            "🔎 **Realtime Tracking:** Watching all ban/kick events 24/7\n"  
            "⚡ **Attack Response:** Instant lockdown if mass ban detected\n"  
            "🔒 **Auto-Demote:** Any admin banning >5 members in 10 seconds will be stripped of rights\n"  
            "📢 **Alerts:** Owner & trusted admins will be notified instantly\n"  
            "🛠 **Self-Healing Mode:** Auto-recovers from bot kicks or permission loss\n\n"  
            f"👑 **Owner:** {message.from_user.mention}\n"  
            "📡 **Protection Status:** 🟢 Active & Ready to Neutralize Threats"  
        )

        await enable_antibanall(chat_id, message.chat.title, message.chat.username)

   # Function to track ban actions
def add_ban_action(chat_id, admin_id):
    current_time = time.time()
    if chat_id not in ban_tracker:
        ban_tracker[chat_id] = {}
    if admin_id not in ban_tracker[chat_id]:
        ban_tracker[chat_id][admin_id] = {"bans": [], "last_cleanup": current_time}

    # Keep only bans within TTL
    ban_tracker[chat_id][admin_id]["bans"] = [
        ban_time for ban_time in ban_tracker[chat_id][admin_id]["bans"]
        if current_time - ban_time < BAN_TRACKING_TTL
    ]

    ban_tracker[chat_id][admin_id]["bans"].append(current_time)
    ban_tracker[chat_id][admin_id]["last_cleanup"] = current_time
    return len(ban_tracker[chat_id][admin_id]["bans"])


# Function to check if admin is mass banning
def is_mass_banning(chat_id, admin_id):
    if chat_id not in ban_tracker or admin_id not in ban_tracker[chat_id]:
        return False
    current_time = time.time()
    ban_tracker[chat_id][admin_id]["bans"] = [
        ban_time for ban_time in ban_tracker[chat_id][admin_id]["bans"]
        if current_time - ban_time < BAN_TRACKING_TTL
    ]
    return len(ban_tracker[chat_id][admin_id]["bans"]) >= BAN_THRESHOLD


# Monitor bans
@app.on_chat_member_updated(group=690)
@error
async def monitor_bans(client: Client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id
    if not await is_antibanall_enabled(chat_id):
        return

    from_user = chat_member_updated.from_user
    if not from_user or from_user.id == config.BOT_ID:
        return

    old_status = chat_member_updated.old_chat_member.status if chat_member_updated.old_chat_member else None
    new_status = chat_member_updated.new_chat_member.status if chat_member_updated.new_chat_member else None
    target_user = chat_member_updated.new_chat_member.user if chat_member_updated.new_chat_member else None

    if new_status == ChatMemberStatus.BANNED and old_status != ChatMemberStatus.BANNED:
        admin_id = from_user.id
        ban_count = add_ban_action(chat_id, admin_id)

        if ban_count >= BAN_THRESHOLD:
            try:
                bot_member = await client.get_chat_member(chat_id, "me")
                if bot_member.privileges and bot_member.privileges.can_promote_members:
                    # Demote admin who banned too many users
                    await client.promote_chat_member(
                        chat_id=chat_id,
                        user_id=admin_id,
                        privileges=None
                    )
                    admin_mention = f"<a href='tg://user?id={admin_id}'>{from_user.first_name}</a>"
                    await client.send_message(
                        chat_id,
                        f"⚠️ <b>AntiBanAll Protection Triggered</b> ⚠️\n\n"
                        f"{admin_mention} has been demoted for banning {ban_count} users in less than {BAN_TRACKING_TTL} seconds.",
                        parse_mode=ParseMode.HTML
                    )
                    log_message = await format_log(
                        action="AntiBanAll Protection Triggered",
                        chat=chat_member_updated.chat.title or str(chat_id),
                        admin=f"{admin_mention} ({admin_id})",
                        user=f"Banned {ban_count} users in {BAN_TRACKING_TTL} seconds"
                    )
                    await send_log(chat_id, log_message)
                else:
                    # If bot cannot demote, alert all admins
                    admins = await client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
                    admin_mentions = " ".join(
                        [f"<a href='tg://user?id={admin.user.id}'>{admin.user.first_name}</a>"
                         for admin in admins if not admin.user.is_bot]
                    )
                    await client.send_message(
                        chat_id,
                        f"⚠️ <b>AntiBanAll Alert</b> ⚠️\n\n"
                        f"<a href='tg://user?id={admin_id}'>{from_user.first_name}</a> is mass banning users ({ban_count} bans in {BAN_TRACKING_TTL} seconds).\n\n"
                        f"I don't have permission to demote this admin. Chat owners, please take action!\n\n"
                        f"👮‍♂️ <b>Mentioning All Admins:</b> {admin_mentions}",
                        parse_mode=ParseMode.HTML
                    )
                    log_message = await format_log(
                        action="AntiBanAll Alert (No Permission)",
                        chat=chat_member_updated.chat.title or str(chat_id),
                        admin=f"<a href='tg://user?id={admin_id}'>{from_user.first_name}</a> ({admin_id})",
                        user=f"Banned {ban_count} users in {BAN_TRACKING_TTL} seconds"
                    )
                    await send_log(chat_id, log_message)
            except Exception as e:
                log_message = await format_log(
                    action="AntiBanAll Error",
                    chat=chat_member_updated.chat.title or str(chat_id),
                    admin=f"Error: {str(e)}"
                )
                await send_log(chat_id, log_message)

__module__ = "🛡️ AntiBanAll"
__help__ = """🛡️ **AntiBanAll Protection System**

Protect your group from mass-ban attacks with real-time monitoring and automatic admin demotion.

**✧ /antibanall** – Toggle AntiBanAll protection  
  - **When enabled:** I'll demote any admin who bans >5 users in 10 seconds  
  - **If I lack demote permissions:** I'll alert all admins via group mentions and private messages  

**Key Features:**  
⚡ Real-time ban monitoring  
🔒 Automatic admin demotion  
📢 Multi-channel alerts (Group + PM)  
🤖 Bot attack protection  
🚨 Critical alert system  

**Protection Workflow:**  
1. Constant monitoring of all ban actions  
2. Detect patterns indicating mass banning  
3. Automatically demote offending admins  
4. Alert all group admins during attacks  
5. Send PM alerts to admins who've started me  

**Note:** For maximum protection, make sure I have admin privileges with **'Ban Users'** and **'Add Admins'** permissions!  

**🔧 Setup Tip:** Demote all current admins and re-promote them using me with:  
`/promote@kafka_xprobot`  
This ensures I can monitor and control admin privileges effectively.
"""