import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Yumeko import app  # Your main Pyrogram bot client

# Button shown under each reply
BUTTON = InlineKeyboardMarkup(
    [[InlineKeyboardButton("❓ What Is This", url="https://t.me/echoclubx")]]
)

# Media links
HOT = "https://telegra.ph/file/20d6f58b629bfc8303c16.mp4"
SMEXY = "https://telegra.ph/file/bc1aef9db142d775de4af.mp4"
LEZBIAN = "https://telegra.ph/file/4bfaffdaa56a5eb515ed3.mp4"
BIGBALL = "https://telegra.ph/file/3017e2197e5f2b084f34b.mp4"
LANG = "https://telegra.ph/file/a922b51801f22d7859542.mp4"
CUTIE = "https://telegra.ph/file/f7493019b920c58905e8f.mp4"

def get_mention(user) -> str:
    return f"[{user.first_name}](tg://user?id={user.id})"

# Fun commands with media + templates
FUN_COMMANDS = [
    ("horny", "🔥", HOT, "is {}% Horny!"),
    ("gay", "🏳️‍🌈", SMEXY, "is {}% Gay!"),
    ("lezbian", "💜", LEZBIAN, "is {}% Lezbian!"),
    ("boobs", "🍒", BIGBALL, "'s Boobs Size is {}!"),
    ("cock", "🍆", LANG, "'s Cock Size is {}cm"),
    ("cute", "🍑", CUTIE, "is {}% Cute"),
]

# Register handlers dynamically
for cmd, emoji, file_link, text_template in FUN_COMMANDS:
    @app.on_message(filters.command(cmd, prefixes=["/", "!"]))
    async def command_handler(client, message: Message,
                              emoji=emoji, file_link=file_link, text_template=text_template):
        user = message.from_user
        mention = get_mention(user)
        value = random.randint(1, 100)

        # Build caption
        reply_text = f"**{emoji}** {mention} {text_template.format(value)}"

        # Send video with caption + button
        await message.reply_video(
            video=file_link,
            caption=reply_text,
            reply_markup=BUTTON,
            quote=True
        )

# ---------------- Module Help ----------------
__module__ = "Fun-Commands"

__help__ = """
This module is just for **Fun** 😏 Don't take it seriously.

**Commands:**
   ✧ `/horny` — Check your current hornyness
   ✧ `/gay` — Check your gayness
   ✧ `/lezbian` — Check your lezbianess
   ✧ `/boobs` — Check your boobs size
   ✧ `/cock` — Check your cock size
   ✧ `/cute` — Check your cuteness

Note: Inspired by @HowAllBot — Just for fun.
"""