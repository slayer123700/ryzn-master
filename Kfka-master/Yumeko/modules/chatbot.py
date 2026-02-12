from Yumeko import app, CHATBOT_GROUP
from Yumeko.database.chatbotdb import enable_chatbot, disable_chatbot, is_chatbot_enabled
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import config
from Yumeko.decorator.chatadmin import chatadmin
from pyrogram.enums import ChatAction
import httpx
from Yumeko.decorator.save import save
from Yumeko.decorator.errors import error


# ─────────────────────────────
# Toggle chatbot in groups
# ─────────────────────────────
@app.on_message(filters.command("chatbot", prefixes=config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def chatbot_handler(client: Client, message: Message):
    chat_id = message.chat.id

    if await is_chatbot_enabled(chat_id):
        # Already enabled → show disable button
        button = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔴 Disable Chatbot", callback_data=f"disable_chatbot:{chat_id}")],
                [InlineKeyboardButton("🗑️ Close", callback_data="delete")]
            ]
        )
        await message.reply_text(
            "**📢 Chatbot is currently enabled in this chat.**",
            reply_markup=button
        )
    else:
        # Disabled → show enable button
        button = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🟢 Enable Chatbot", callback_data=f"enable_chatbot:{chat_id}")],
                [InlineKeyboardButton("🗑️ Close", callback_data="delete")]
            ]
        )
        await message.reply_text(
            "**📢 Chatbot is currently disabled in this chat.**",
            reply_markup=button
        )


# ─────────────────────────────
# Callback buttons
# ─────────────────────────────
@app.on_callback_query(filters.regex("^(enable_chatbot|disable_chatbot):"))
@chatadmin
@error
async def toggle_chatbot(client: Client, callback_query: CallbackQuery):
    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)

    try:
        chat = await client.get_chat(chat_id)
        title = chat.title
        username = chat.username
    except Exception:
        title = "Unknown"
        username = None

    if action == "enable_chatbot":
        await enable_chatbot(chat_id, title, username)
        await callback_query.message.edit_text("**🟢 Chatbot has been enabled for this chat.**")
    elif action == "disable_chatbot":
        await disable_chatbot(chat_id)
        await callback_query.message.edit_text("**🔴 Chatbot has been disabled for this chat.**")


# ─────────────────────────────
# Chatbot handler (replies only if user replies to bot)
# ─────────────────────────────
@app.on_message((filters.group | filters.private) & filters.reply, group=CHATBOT_GROUP)
@error
@save
async def handle_chatbot(client: Client, message: Message):
    if not message.from_user:
        return

    if not await is_chatbot_enabled(message.chat.id):
        return

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return

    # Only respond if user replies to the bot’s own message
    if message.reply_to_message.from_user.id != config.BOT_ID:
        return

    await client.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    m = message.text

    try:
        async with httpx.AsyncClient(timeout=15) as session:
            resp = await session.get(
                "http://api.brainshop.ai/get",
                params={
                    "bid": 176809,
                    "key": "lbMN8CXTGzhn1NKG",
                    "uid": message.from_user.id,
                    "msg": m,
                },
            )
            response_data = resp.json()
            bot_response = response_data.get("cnt", "I couldn't process that right now.")
    except httpx.RequestError as e:
        print(f"Error fetching chatbot response: {e}")
        bot_response = None
    except Exception as e:
        print(f"Unexpected error: {e}")
        bot_response = None

    if bot_response is None:
        await message.reply_text(
            "❌ Chatbot is facing issues and has been disabled for now. Please contact the bot support."
        )
        await disable_chatbot(message.chat.id)
        return

    await message.reply_text(bot_response)


# ─────────────────────────────
# Help metadata
# ─────────────────────────────
__module__ = "Chatbot"
__help__ = """
**Chatbot Module**

• `/chatbot` — Enable or disable chatbot in your group  
(Owner/Admin only)

💡 Reply to the bot’s message with text, and the chatbot will respond.
"""