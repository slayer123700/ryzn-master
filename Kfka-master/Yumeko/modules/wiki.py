import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app

@app.on_message(filters.command("wiki", prefixes=["/", "!"]))
async def wiki(_, message: Message):
    """Search Wikipedia for a query."""
    if message.reply_to_message:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("`Usage: /wiki <query>`")

    try:
        summary = wikipedia.summary(text)
    except DisambiguationError as e:
        return await message.reply_text(
            f"⚠️ Disambiguation pages found! Adjust your query.\n<i>{e}</i>",
            parse_mode="html",
        )
    except PageError as e:
        return await message.reply_text(f"<code>{e}</code>", parse_mode="html")

    result = f"<b>{text}</b>\n\n<i>{summary}</i>\n"
    result += f'<a href="https://en.wikipedia.org/wiki/{text.replace(" ", "%20")}">Read more...</a>'

    if len(result) > 4000:
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(result)
        with open("result.txt", "rb") as f:
            await message.reply_document(f)
    else:
        await message.reply_text(result, parse_mode="html", disable_web_page_preview=True)

# ---------------- Module Help ----------------
__module__ = "Wiki"

__help__ = """*Wikipedia*

❍ `/wiki <text>` — Search Wikipedia for the given text and get a summary.
❍ Reply `/wiki` to a message — Searches the text in the replied message.
"""