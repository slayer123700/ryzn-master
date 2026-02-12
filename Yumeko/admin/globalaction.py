from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired, FloodWait, UserAdminInvalid
import random
import asyncio
from datetime import datetime

from Yumeko import app
from Yumeko.decorator.botadmin import hokage, botadmin
from Yumeko.decorator.errors import error
from Yumeko.decorator.save import save
from Yumeko.database.global_actions_db import (
    add_to_gban,
    add_to_gmute,
    remove_from_gban,
    remove_from_gmute,
    is_user_gbanned,
    is_user_gmuted,
    get_all_gmuted_users,
    get_all_gbanned_users,
    save_banned_chats,
    get_banned_chats,
    get_common_chat_ids,
)
from Yumeko.database.common_chat_db import get_common_chat_ids
from config import config

OWNER_ID = 6125202012  # Owner Telegram user ID


# ---------------------- HELPERS ----------------------

async def send_global_log(client: Client, action: str, target_user, performed_by, time_taken: float):
    """Send a nicely formatted log to owner PM."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    log_msg = (
        "🚨 Global Action Log 🚨\n\n"
        f"Action: {action}\n"
        f"Target User: [{target_user.first_name}](tg://user?id={target_user.id}) ({target_user.id})\n"
        f"Username: @{target_user.username if target_user.username else 'No Username'}\n"
        f"Performed By: [{performed_by.first_name}](tg://user?id={performed_by.id}) ({performed_by.id})\n"
        f"⏱ Time Taken: {time_taken}s\n"
        f"📅 Time: {now}\n\n"
        f"#LOG #{action.upper()}"
    )
    try:
        await client.send_message(OWNER_ID, log_msg, disable_web_page_preview=True)
    except Exception as e:
        print(f"Failed to send log to owner: {e}")


async def extract_user_info(client: Client, message: Message, args):
    """Extract user info from reply or args."""
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user
        elif args:
            return await client.get_users(args[0])
        else:
            return None
    except Exception as e:
        print(f"Error in extract_user_info: {e}")
        return None


async def animation_steps(msg: Message, steps: list, delay: float = 1.2):
    """Edit message with multiple steps to simulate animation."""
    for step in steps:
        await msg.edit_text(step)
        await asyncio.sleep(delay)


def build_final_message(action: str, target_user, performed_by, time_taken: float):
    """Return formatted success message."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"✅ {action} Successful\n\n"
        f"👤 Name: [{target_user.first_name}](tg://user?id={target_user.id})\n"
        f"🆔 ID: {target_user.id}\n"
        f"🔗 Username: @{target_user.username if target_user.username else 'No Username'}\n"
        f"⚡ Action: {action}\n"
        f"👑 By: [{performed_by.first_name}](tg://user?id={performed_by.id})\n"
        f"⏱ Time Taken: {time_taken}s\n"
        f"📅 Time: {now}"
    )


def format_user_list_detailed(users, title):
    """Format GBan/GMute list with emoji style."""
    if not users:
        return f"⚠️ {title}\n\n_No users found in this list._"

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = (
        f"🔰 {title} 🔰\n"
        f"📅 _As of {now}_\n\n"
        "═══════════════════════\n"
    )

    lines = []
    for idx, user in enumerate(users, 1):
        name = user.get("first_name", "Unknown")
        username = f"@{user.get('username')}" if user.get("username") else "No Username"
        user_id = user.get("id", "Unknown")
        lines.append(
            f"➤ {idx}. {name} {username}\n"
            f"   🆔 {user_id}\n"
            "───────────────────────"
        )

    footer = "\n⚠️ Use with caution! Global actions affect all groups where the bot is present."
    return header + "\n".join(lines) + footer


# ---------------------- COMMANDS ----------------------

@app.on_message(filters.command("gmute", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def gmute_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)
    if not user:
        return await message.reply_text("⚠️ Please provide a valid user ID, username, or reply to a user.")
    if await is_user_gmuted(user.id):
        return await message.reply_text(f"🔇 {user.first_name or user.id} is already globally muted.")

    msg = await message.reply_text(f"Initializing Global Mute for {user.first_name}...")
    await animation_steps(msg, [
        "🔍 Checking permissions...",
        "✅ Permissions verified...",
        "📡 Applying Global Mute...",
        "💾 Saving to database..."
    ])

    start_time = datetime.utcnow()
    await add_to_gmute(user.id, user.first_name, user.username)
    time_taken = round((datetime.utcnow() - start_time).total_seconds(), 2)

    await msg.edit_text(build_final_message("Global Mute", user, message.from_user, time_taken), disable_web_page_preview=True)
    await send_global_log(client, "GMute", user, message.from_user, time_taken)


@app.on_message(filters.command("ungmute", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def ungmute_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)
    if not user:
        return await message.reply_text("⚠️ Please provide a valid user ID, username, or reply to a user.")
    if not await is_user_gmuted(user.id):
        return await message.reply_text(f"🔈 {user.first_name or user.id} is not globally muted.")

    msg = await message.reply_text(f"Initializing Global Unmute for {user.first_name}...")
    await animation_steps(msg, [
        "🔍 Checking permissions...",
        "✅ Permissions verified...",
        "📡 Removing Global Mute...",
        "💾 Updating database..."
    ])

    start_time = datetime.utcnow()
    await remove_from_gmute(user.id)
    time_taken = round((datetime.utcnow() - start_time).total_seconds(), 2)

    await msg.edit_text(build_final_message("Global Unmute", user, message.from_user, time_taken), disable_web_page_preview=True)
    await send_global_log(client, "UnGMute", user, message.from_user, time_taken)


@app.on_message(filters.command("gban", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def gban_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)
    if not user:
        return await message.reply_text("⚠️ Please provide a valid user ID, username, or reply to a user.")
    if await is_user_gbanned(user.id):
        return await message.reply_text(f"🚫 {user.first_name or user.id} is already globally banned.")

    msg = await message.reply_text(f"Initializing Global Ban for {user.first_name}...")
    await animation_steps(msg, [
        "🔍 Checking permissions...",
        "✅ Permissions verified...",
        "📡 Applying Global Ban to all chats...",
        "💾 Saving ban records..."
    ])

    start_time = datetime.utcnow()
    await add_to_gban(user.id, user.first_name, user.username)
    common_chats = await get_common_chat_ids(user.id)
    for chat_id in common_chats:
        try:
            await client.ban_chat_member(chat_id, user.id)
        except Exception:
            pass
    await save_banned_chats(user.id, common_chats)
    time_taken = round((datetime.utcnow() - start_time).total_seconds(), 2)

    await msg.edit_text(build_final_message("Global Ban", user, message.from_user, time_taken), disable_web_page_preview=True)
    await send_global_log(client, "GBan", user, message.from_user, time_taken)


@app.on_message(filters.command("ungban", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def ungban_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)
    if not user:
        return await message.reply_text("⚠️ Please provide a valid user ID, username, or reply to a user.")
    if not await is_user_gbanned(user.id):
        return await message.reply_text(f"✅ {user.first_name or user.id} is not globally banned.")

    msg = await message.reply_text(f"Initializing Global Unban for {user.first_name}...")
    await animation_steps(msg, [
        "🔍 Checking permissions...",
        "✅ Permissions verified...",
        "📡 Removing Global Ban from all chats...",
        "💾 Updating ban records..."
    ])

    start_time = datetime.utcnow()
    await remove_from_gban(user.id)
    banned_chats = await get_banned_chats(user.id)
    for chat_id in banned_chats:
        try:
            await client.unban_chat_member(chat_id, user.id)
        except Exception:
            pass
    time_taken = round((datetime.utcnow() - start_time).total_seconds(), 2)

    await msg.edit_text(build_final_message("Global Unban", user, message.from_user, time_taken), disable_web_page_preview=True)
    await send_global_log(client, "UnGBan", user, message.from_user, time_taken)


@app.on_message(filters.command("zaryab", prefixes=config.COMMAND_PREFIXES))
async def zaryab_gban_gmute(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ You are not authorized to use this command.")

    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)
    if not user:
        return await message.reply_text("❌ Please provide a valid user by replying or username/ID.")

    msg = await message.reply_text(f"Initiating Global Ban & Mute for {user.first_name}...")
    await animation_steps(msg, [
        "🔍 Checking permissions...",
        "✅ Permissions verified...",
        "📡 Applying GBan & GMute...",
        "💾 Saving all records..."
    ])

    start_time = datetime.utcnow()
    await add_to_gban(user.id, user.first_name, user.username)
    await add_to_gmute(user.id, user.first_name, user.username)
    common_chats = await get_common_chat_ids(user.id)
    for chat_id in common_chats:
        try:
            await client.ban_chat_member(chat_id, user.id)
        except Exception:
            pass
    await save_banned_chats(user.id, common_chats)
    time_taken = round((datetime.utcnow() - start_time).total_seconds(), 2)

    await msg.edit_text(build_final_message("GBan + GMute", user, message.from_user, time_taken), disable_web_page_preview=True)
    await send_global_log(client, "GBan+GMute", user, message.from_user, time_taken)


# ---------------------- LIST COMMANDS ----------------------

@app.on_message(filters.command("gbanned", prefixes=config.COMMAND_PREFIXES))
@botadmin
@error
@save
async def list_gbanned_users(client: Client, message: Message):
    users = await get_all_gbanned_users()
    formatted = format_user_list_detailed(users, "Globally Banned Users")
    await message.reply_text(
        formatted,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Delete", callback_data="delete_msg")]])
    )


@app.on_message(filters.command("gmuted", prefixes=config.COMMAND_PREFIXES))
@botadmin
@error
@save
async def list_gmuted_users(client: Client, message: Message):
    users = await get_all_gmuted_users()
    formatted = format_user_list_detailed(users, "Globally Muted Users")
    await message.reply_text(
        formatted,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Delete", callback_data="delete_msg")]])
    )


# ---------------------- DELETE BUTTON HANDLER ----------------------

@app.on_callback_query(filters.regex("^delete_msg$"))
async def delete_list_message(client: Client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.answer()  # Silent, no popup