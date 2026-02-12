from pyrogram import Client, filters
from pyrogram.types import Message
from Yumeko import app
import config
from pyrogram.enums import MessageEntityType
from Yumeko.decorator.errors import error
from Yumeko.database.common_chat_db import get_common_chat_count
from Yumeko.database.afk_db import is_user_afk
from Yumeko.database.global_actions_db import is_user_gbanned , is_user_gmuted
from Yumeko.database.user_info_db import get_user_infoo
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import PeerIdInvalid
from asyncio import sleep

@app.on_message(filters.command("id", prefixes=config.config.COMMAND_PREFIXES))
@error
async def get_id(client: Client, message: Message):
    """
    Handles the /id command, providing Chat ID and user IDs based on context.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    reply = message.reply_to_message
    entities = message.entities
    command_args = message.command[1:] if len(message.command) > 1 else []

    # Base response
    response = [f"**Chat ID:** `{chat_id}`\n", f"**Your ID:** `{user_id}`\n"]

    # Handle replies
    if reply:
        if reply.forward_from_chat:  # Forwarded message
            response.append(
                f"**Forwarded Chat ID:** `{reply.forward_from_chat.id}`\n"
            )
        elif reply.from_user:  # Reply to a user
            response.append(
                f"**Replied User ID:** `{reply.from_user.id}` ({reply.from_user.mention()})\n"
            )

    # Handle text mentions
    if entities:
        for entity in entities:
            if entity.type == MessageEntityType.TEXT_MENTION:
                response.append(
                    f"**Mentioned User ID:** `{entity.user.id}` ({entity.user.mention()})\n"
                )
                break

    # Handle username arguments
    if command_args:
        username = command_args[0].strip("@")
        try:
            user_details = await client.get_users(username)
            response.append(
                f"**Username ID:** `{user_details.id}` ({user_details.mention()})\n"
            )
        except Exception:
            response.append("")

    # Final fallback: default response
    if len(response) == 2:  # No additional info added
        response.append("")

    x = await message.reply_text("".join(response))
    await sleep(180)
    await x.delete()

                 
__module__ = "𝖨D"


__help__ = """**𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
  ✧ `/𝗂𝖽`**:** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗍 𝖨𝖣 𝖺𝗇𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣.
 
  ✧ `/𝗂𝖽 <𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾>`**:** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋 (𝖼𝖺𝗌𝖾-𝗂𝗇𝗌𝖾𝗇𝗌𝗂𝗍𝗂𝗏𝖾 𝗌𝖾𝖺𝗋𝖼𝗁) 𝖺𝗅𝗈𝗇𝗀 𝗐𝗂𝗍𝗁 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗍 𝖨𝖣 𝖺𝗇𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣.
 
  ✧ `/𝗂𝖽` **(replied to a user's message):** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗐𝗁𝗈𝗌𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗂𝗌 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝖳𝗈.
"""