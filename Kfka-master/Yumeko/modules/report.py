from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app  # your client instance

__module__ = "Report"
__help__ = """
**Admin Alerts**

Commands/Triggers: `/admin`, `/admins`, `/report`, `@admin`, `@admins`

- Tags all group admins in a single message.
"""

TRIGGER_FILTER = filters.group & (
    filters.command(["admin", "admins", "report"], prefixes=["/", "!", ".", "?"])
    | filters.regex(r"(?i)@admins?")
)


@app.on_message(TRIGGER_FILTER)
async def alert_admins(client, message: Message):
    try:
        members = [m async for m in client.get_chat_administrators(message.chat.id)]
    except Exception as e:
        return await message.reply_text(f"⚠️ Could not fetch admins: `{e}`")

    # Get only real users (skip bots)
    admins = [m.user for m in members if not m.user.is_bot]

    if not admins:
        return await message.reply_text("⚠️ No admins found to notify.")

    reporter = message.from_user.mention if message.from_user else "Someone"

    # Build tags using usernames (fallback to ID mention if no username)
    tags = []
    for admin in admins:
        if admin.username:
            tags.append(f"@{admin.username}")
        else:
            tags.append(f"[{admin.first_name}](tg://user?id={admin.id})")

    tags_text = " ".join(tags)

    await message.reply_text(
        f"🚨 Reported to admins by {reporter}\n{tags_text}",
        quote=True,
        disable_web_page_preview=True,
    )