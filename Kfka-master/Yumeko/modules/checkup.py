from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired, RPCError
from pyrogram.enums import ChatMemberStatus

from Yumeko import app, config  # Yumeko’s app + config loader

TECH_TEAM_ID = config.OWNER_ID  # Tech team or Owner ID

__module__ = "Checkup"
__help__ = """
🔍 **Group Checkup**
Admins can report group issues to the tech team.

**Usage:**
- `/checkup [optional reason]` → Report a problem with optional explanation.
"""


@app.on_message(filters.command("checkup", prefixes=config.COMMAND_PREFIXES) & filters.group)
async def checkup_command(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Verify admin
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return await message.reply_text("❌ Only group admins can run this command.")
    except RPCError:
        return await message.reply_text("⚠️ Could not verify your admin status.")

    # Verify bot’s permission
    try:
        me = await client.get_me()
        bot_member = await client.get_chat_member(chat_id, me.id)
        if not getattr(bot_member.privileges, "can_invite_users", False):
            return await message.reply_text("⚠️ I need **Invite Users** permission to share the invite link.")
    except RPCError:
        return await message.reply_text("⚠️ Could not verify my permissions.")

    # Extract optional reason
    reason = message.text.partition(" ")[2].strip() or "No reason provided."

    # Export invite link
    try:
        invite_link = await client.export_chat_invite_link(chat_id)
    except ChatAdminRequired:
        return await message.reply_text("❌ I don't have permission to export invite links.")
    except Exception as e:
        return await message.reply_text(f"❌ Failed to get invite link: {e}")

    # Report text (only reason and reporter info)
    report_text = (
        f"🔔 **New Problem Report**\n\n"
        f"👤 Reported by: {message.from_user.mention} (`{user_id}`)\n"
        f"📌 Group: **{message.chat.title}** (`{chat_id}`)\n"
        f"📝 Reason: {reason}"
    )

    # Buttons (link + actions)
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔗 Join Group", url=invite_link)],
            [
                InlineKeyboardButton("🔍 Check Group", callback_data=f"checkgroup|{chat_id}|{user_id}"),
                InlineKeyboardButton("✅ Solved", callback_data=f"solved|{chat_id}|{user_id}")
            ]
        ]
    )

    # Send to tech team
    try:
        await client.send_message(TECH_TEAM_ID, report_text, reply_markup=buttons)
    except Exception as e:
        return await message.reply_text(f"❌ Failed to notify tech team: {e}")

    await message.reply_text("✅ Problem report sent to the tech team. They will check soon.")


@app.on_callback_query(filters.regex(r"^(checkgroup|solved)\|"))
async def checkup_callback(client, query: CallbackQuery):
    action, chat_id_str, reporter_id_str = query.data.split("|")
    chat_id = int(chat_id_str)
    reporter_id = int(reporter_id_str)

    # Only allow tech team/owner
    if query.from_user.id != TECH_TEAM_ID:
        await query.answer("❌ You are not authorized to use this.", show_alert=True)
        return

    if action == "checkgroup":
        try:
            chat = await client.get_chat(chat_id)
            member_count = await client.get_chat_members_count(chat_id)

            info_text = (
                f"🔍 **Group Info**\n"
                f"📌 Name: {chat.title}\n"
                f"🆔 ID: `{chat.id}`\n"
                f"👥 Members: {member_count}\n"
                f"📂 Type: {chat.type}"
            )
            await query.answer("Group info loaded ✅", show_alert=True)
            # ✅ Keep original text, just reply with info
            await query.message.reply_text(info_text)
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)

    elif action == "solved":
        # Notify group
        try:
            await client.send_message(
                chat_id,
                f"✅ Problem reported by <a href='tg://user?id={reporter_id}'>this user</a> "
                f"has been marked as solved by {query.from_user.mention}.",
                parse_mode="html"
            )
        except Exception:
            pass

        # Notify reporter
        try:
            await client.send_message(
                reporter_id,
                f"✅ Your problem report for group `{chat_id}` has been marked as solved by {query.from_user.mention}.",
                parse_mode="html"
            )
        except Exception:
            pass

        await query.answer("Marked as solved ✅", show_alert=True)
        # ✅ Instead of replacing the text, just append solved note
        await query.message.edit_reply_markup(None)  # remove buttons
        await query.message.reply_text("✅ This problem has been resolved.")