import json
import os
import logging
from typing import Dict, List
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from Yumeko import app as pgram
from config import config
from Yumeko.decorator.errors import error
from Yumeko.decorator.save import save

OWNER_ID = config.OWNER_ID
SPECIAL_USER_ID = 7876439267  # Replace with your special user ID
sudoers_file = "sudoers.json"
logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def load_roles() -> Dict[str, List[int]]:
    try:
        if not os.path.exists(sudoers_file):
            with open(sudoers_file, "w") as f:
                default_roles = {"Hokages": [], "Jonins": [], "Chunins": [], "Genins": []}
                json.dump(default_roles, f, indent=4)
            return default_roles
        with open(sudoers_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading roles: {e}")
        return {"Hokages": [], "Jonins": [], "Chunins": [], "Genins": []}

def save_roles(data: Dict) -> None:
    try:
        with open(sudoers_file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving roles: {e}")

def ensure_owner_is_hokage() -> None:
    roles = load_roles()
    if OWNER_ID not in roles["Hokages"]:
        roles["Hokages"].append(OWNER_ID)
        save_roles(roles)

async def get_user_info(client: Client, user_id: int) -> str:
    try:
        user = await client.get_users(user_id)
        return f"{user.mention} ({user_id})"
    except Exception as e:
        logger.warning(f"Couldn't fetch user {user_id}: {e}")
        return f"Unknown User ({user_id})"

def get_hierarchy_level(user_id: int) -> int:
    if user_id == OWNER_ID:
        return 0
    if user_id == SPECIAL_USER_ID:
        return 0
    roles = load_roles()
    if user_id in roles["Hokages"]:
        return 1
    if user_id in roles["Jonins"]:
        return 2
    if user_id in roles["Chunins"]:
        return 3
    if user_id in roles["Genins"]:
        return 4
    return 999

def get_allowed_roles(assigner_id: int) -> List[str]:
    assigner_level = get_hierarchy_level(assigner_id)
    if assigner_level == 0:
        return ["Hokage", "Jonin", "Chunin", "Genin"]
    if assigner_level == 1:
        return ["Jonin", "Chunin", "Genin"]
    if assigner_level == 2:
        return ["Chunin", "Genin"]
    if assigner_level == 3:
        return ["Genin"]
    return []

async def send_role_log(client: Client, action: str, role: str, target_id: int, sender_id: int):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    target_info = await get_user_info(client, target_id)
    sender_info = await get_user_info(client, sender_id)
    log_text = (
        f"📢 Role {action} Log 📢\n\n"
        f"• Action: {action}\n"
        f"• Role: {role}\n"
        f"• Target User: {target_info}\n"
        f"• Performed By: {sender_info}\n"
        f"🕐 Time: {now}"
    )
    for user_id in {OWNER_ID, SPECIAL_USER_ID}:
        try:
            await client.send_message(user_id, log_text)
        except Exception:
            pass

@pgram.on_message(filters.command("assign", prefixes=config.COMMAND_PREFIXES))
@error
@save
async def assign_role(client: Client, message: Message):
    ensure_owner_is_hokage()
    sender = message.from_user
    if sender.id != OWNER_ID and sender.id != SPECIAL_USER_ID and get_hierarchy_level(sender.id) > 3:
        await message.reply("❌ You don't have permission to use this command.")
        return
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target = await client.get_users(target_id)
        except Exception:
            await message.reply("❌ Couldn't find that user.")
            return
    else:
        await message.reply("🔍 Please reply to a user or provide a valid UserID.")
        return

    target_level = get_hierarchy_level(target.id)
    sender_level = get_hierarchy_level(sender.id)

    if sender.id not in (OWNER_ID, SPECIAL_USER_ID):
        if target_level <= sender_level:
            await message.reply("⛔ You can only assign roles to users below your hierarchy level.")
            return

    allowed_roles = get_allowed_roles(sender.id)
    if not allowed_roles:
        await message.reply("❌ You don't have permission to assign any roles.")
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"🛡️ {role}",
            callback_data=f"assign:{role}:{target.id}:{sender.id}"
        )] for role in allowed_roles
    ])

    target_info = await get_user_info(client, target.id)
    await message.reply(
        f"🌟 Assigning Role to {target_info}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "Choose a role to assign:",
        reply_markup=buttons
    )

@pgram.on_callback_query(filters.regex(r"^assign:(.+?):(\d+):(\d+)$"))
@error
@save
async def handle_assign_callback(client: Client, callback: CallbackQuery):
    ensure_owner_is_hokage()
    role, target_id, sender_id = callback.data.split(":")[1:]
    target_id = int(target_id)
    sender_id = int(sender_id)
    if callback.from_user.id != sender_id:
        await callback.answer("🚫 Action not permitted!", show_alert=True)
        return

    roles = load_roles()
    allowed_roles = get_allowed_roles(sender_id)
    if role not in allowed_roles:
        await callback.answer("❌ Permission denied for this role!", show_alert=True)
        return

    # Remove existing roles
    for existing_role in ["Hokages", "Jonins", "Chunins", "Genins"]:
        if target_id in roles[existing_role]:
            roles[existing_role].remove(target_id)

    role_key = f"{role}s" if role != "Genin" else "Genins"
    roles[role_key].append(target_id)
    save_roles(roles)

    # Log assignment
    await send_role_log(client, "Assignment", role, target_id, sender_id)

    target_info = await get_user_info(client, target_id)
    await callback.edit_message_text(
        f"✅ Successfully Assigned\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"• User: {target_info}\n"
        f"• Role: {role}\n"
        f"• Assigned by: {callback.from_user.mention}"
    )

@pgram.on_message(filters.command("unassign", prefixes=config.COMMAND_PREFIXES))
@error
@save
async def remove_role(client: Client, message: Message):
    ensure_owner_is_hokage()
    sender = message.from_user
    if sender.id != OWNER_ID and sender.id != SPECIAL_USER_ID and get_hierarchy_level(sender.id) > 3:
        await message.reply("❌ You don't have permission to use this command.")
        return
    try:
        if message.reply_to_message:
            target = message.reply_to_message.from_user
        else:
            target_id = int(message.command[1])
            target = await client.get_users(target_id)
    except Exception:
        await message.reply("❌ Invalid user or user ID.")
        return

    if target.id == OWNER_ID:
        await message.reply("ℹ️ Roles 'removed' from Owner (but Owner keeps all powers).")
        return

    target_level = get_hierarchy_level(target.id)
    sender_level = get_hierarchy_level(sender.id)
    if sender.id not in (OWNER_ID, SPECIAL_USER_ID):
        if target_level <= sender_level:
            await message.reply("⛔ You can only unassign users below your hierarchy level.")
            return

    roles = load_roles()
    removed = False
    allowed_to_remove = get_allowed_roles(sender.id) + ["Genin"]

    for role in allowed_to_remove:
        role_key = f"{role}s" if role != "Genin" else "Genins"
        if target.id in roles.get(role_key, []):
            roles[role_key].remove(target.id)
            removed = True

    if removed:
        save_roles(roles)
        target_info = await get_user_info(client, target.id)
        await message.reply(
            f"🗑️ Removed Roles\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"• User: {target_info}\n"
            f"• Removed by: {sender.mention}"
        )
        # Log unassignment
        await send_role_log(client, "Unassignment", "Removed Roles", target.id, sender.id)
    else:
        await message.reply("ℹ️ User had no removable roles.")


logger = logging.getLogger(__name__)

@pgram.on_message(filters.command("staffs", prefixes=config.COMMAND_PREFIXES) & filters.user([OWNER_ID, SPECIAL_USER_ID]))
@error
@save
async def list_staffs(client, message):
    try:
        ensure_owner_is_hokage()
        roles = load_roles()

        text = "🔷 𝐒𝐓𝐀𝐅𝐅 𝐇𝐈𝐄𝐑𝐀𝐑𝐂𝐇𝐘 🔷\n\n"
        text += "👑 𝐌𝐘 𝐋𝐎𝐑𝐃\n 神 乙ᴀʀyᴀʙ\n Supreme Leader & Founder\n\n"
        text += "💫 𝐌𝐘 𝐏𝐑𝐈𝐍𝐂𝐄𝐒𝐒\n 𝐒ʏʟᴠɪᴇ \n Crown Princess & Chief Advisor\n\n"
        text += "──────────────\n\n"

        role_display = {
            "Hokages": "🏯 𝐇𝐎𝐊𝐀𝐆𝐄𝐒 (Top Level Commanders)",
            "Jonins": "🗡️ 𝐉𝐎𝐍𝐈𝐍𝐒 (Senior Staff)",
            "Chunins": "⚔️ 𝐂𝐇𝐔𝐍𝐈𝐍𝐒 (Junior Staff)",
            "Genins": "📘 𝐆𝐄𝐍𝐈𝐍𝐒 (Trainees)"
        }

        for role_key, role_name in role_display.items():
            members = roles.get(role_key, [])
            text += f"{role_name}\n"
            if not members:
                text += " └ No members yet\n\n"
                continue
            for i, user_id in enumerate(members, 1):
                prefix = "└" if i == len(members) else "├"
                try:
                    user = await client.get_users(user_id)
                    user_str = f"{user.mention} ({user_id})"
                except:
                    user_str = f"Unknown User ({user_id})"
                text += f" {prefix} {user_str}\n"
            text += "\n"

        text += "─────────────────\n\n"
        text += "📌 Hierarchy reflects experience, responsibility, and trustworthiness."

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑️ Delete", callback_data="staff_delete")]]
        )

        await message.reply(text, reply_markup=buttons)
    except Exception as e:
        logger.error(f"Error in staffs command: {e}")
        await message.reply("❌ An error occurred while fetching staff list.")

@pgram.on_callback_query(filters.regex("^staff_delete$"))
async def delete_staff_message(client, cq):
    try:
        await cq.message.delete()
    except:
        pass