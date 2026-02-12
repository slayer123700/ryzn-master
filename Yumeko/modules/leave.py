from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import PeerIdInvalid, ChannelPrivate, UserNotParticipant
from Yumeko import app

OWNER_ID = 6125202012
PIN_CODE = "1227"

# Temp storage for pending leave approvals
pending_leaves = {}

@app.on_message(filters.command("leave") & filters.user(OWNER_ID))
async def leave_request(client, message):
    # If chat_id passed, use that, else use current chat
    if len(message.command) >= 2:
        chat_id = message.command[1]
    else:
        chat_id = message.chat.id

    try:
        chat = await client.get_chat(chat_id)
        pending_leaves[OWNER_ID] = {"chat_id": chat.id, "title": chat.title}

        # Ask permission in PM
        await client.send_message(
            OWNER_ID,
            f"⚠️ Do you want me to leave?\n\n<b>Chat:</b> {chat.title}\n<b>ID:</b> {chat.id}",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("✅ Yes", callback_data="leave_yes"),
                    InlineKeyboardButton("❌ No", callback_data="leave_no")
                ]]
            )
        )

        if message.chat.type != "private":
            await message.reply_text("📩 Check your PM to approve this leave request.")

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")


@app.on_callback_query(filters.regex("leave_yes"))
async def approve_leave(client, callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        return await callback.answer("Not for you!", show_alert=True)

    await callback.message.edit_text(
        "🔐 Enter the 4-digit PIN to confirm leaving this chat:"
    )
    pending_leaves[OWNER_ID]["waiting_pin"] = True


@app.on_callback_query(filters.regex("leave_no"))
async def reject_leave(client, callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        return await callback.answer("Not for you!", show_alert=True)

    pending_leaves.pop(OWNER_ID, None)
    await callback.message.edit_text("❌ Leave request cancelled.")


@app.on_message(filters.private & filters.user(OWNER_ID))
async def pin_input(client, message):
    # Only if waiting for PIN
    if OWNER_ID not in pending_leaves or not pending_leaves[OWNER_ID].get("waiting_pin"):
        return

    if message.text.strip() == PIN_CODE:
        chat_id = pending_leaves[OWNER_ID]["chat_id"]
        title = pending_leaves[OWNER_ID]["title"]

        try:
            # Send farewell in group
            await client.send_message(chat_id, "My master ordered me to leave, bye world 🌍")
        except Exception:
            pass

        try:
            await client.leave_chat(chat_id)
            await message.reply_text(f"✅ Successfully left {title} ({chat_id})")
        except (PeerIdInvalid, ChannelPrivate, UserNotParticipant):
            await message.reply_text("❌ Failed to leave the chat.")
        except Exception as e:
            await message.reply_text(f"⚠️ Error: {e}")
    else:
        await message.reply_text("❌ Wrong PIN, process failed.")

    # Clear session
    pending_leaves.pop(OWNER_ID, None)

__module__ = "Leave Chat"

__help__ = """**🚪 Leave Chats (Owner Only):**

Allows the bot owner to make the bot leave specific groups or channels.

- **How to use:**
   • `/leave <chat_id>` — Tells the bot to leave the given chat.
   • Only accessible by the bot owner.

- **Example:**
   • `/leave -1001234567890`
     Leaves chat with ID `-1001234567890`.
"""