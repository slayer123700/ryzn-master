from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app

# Make sure you have a secureme module with encrypt and decrypt functions
import secureme

__module__ = "Encrypt & Decrypt"

__help__ = """
*ᴄᴏɴᴠᴇʀᴛs*
 ❍ /encrypt <text>*:* ᴇɴᴄʀʏᴘᴛs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ or reply to a message to encrypt.
 ❍ /decrypt <text>*:* ᴅᴇᴄʀʏᴘᴛs ᴘʀᴇᴠɪᴏᴜsʟʏ ᴇɴᴄʀʏᴘᴛᴇᴅ ᴛᴇxᴛ or reply to a message to decrypt.
"""

# ---------------- ENCRYPT -----------------
@app.on_message(filters.command("encrypt"))
async def encrypt_text(_, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("⚠️ Provide text to encrypt or reply to a message.")
    try:
        encrypted = secureme.encrypt(text)
        await message.reply_text(encrypted)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# ---------------- DECRYPT -----------------
@app.on_message(filters.command("decrypt"))
async def decrypt_text(_, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("⚠️ Provide text to decrypt or reply to a message.")
    try:
        decrypted = secureme.decrypt(text)
        await message.reply_text(decrypted)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")