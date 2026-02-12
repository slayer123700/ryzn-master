from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Yumeko import app  # Your bot instance

OWNER_ID = 7296704435  # 🔹 Replace with your real Telegram numeric ID

__module__ = "Repository"
__help__ = """
**/repo**, **/repository**, **/source** (PM Only)  
Shows the repo sale information, price list, bots under repo, and owner contact.
"""

# Trigger words
TRIGGER_FILTER = filters.command(["repo", "repository", "source"]) & filters.private

@app.on_message(TRIGGER_FILTER)
async def send_repo_info(client: Client, message: Message):
    text = (
        "**💠 Premium Repository 💠**\n\n"
        "🛠 *It took months of hard work to build this masterpiece… and you want it for free?* ✨\n"
        "💼 This repo is **for sale** — price depends on the version you want.\n\n"
        "**💰 Price List:**\n"
        "━━━━━━━━━━━━━\n"
        "🔹 **V1** – `350`\n"
        "🔹 **V3** – `400`\n"
        "🔹 **V4** – `450`\n"
        "🔹 **V5** – `600`\n"
        "🔹 **V6** – `1200`\n"
        "🔹 **V7** – `1500`\n"
        "🔹 **V7.02** – `1700`\n"
        "🔹 **V7.03.01** – `2500` *(🔥 Current Version)*\n"
        "━━━━━━━━━━━━━\n\n"
        "**🤖 Bots Powered by This Repo:**\n"
        "@Kafka_xprobot\n"
        "@Shigaraki_probot\n"
        "@raiden_robot\n"
        "@missmita_bot\n"
        "@TheRebelKidBot\n\n"
        f"📞 **Contact Owner:** [👑 Zaryab](tg://user?id={OWNER_ID})"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🐾 Get Repo", url="https://t.me/echoclubx"),
                InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")
            ]
        ]
    )

    await message.reply_text(text, reply_markup=buttons, disable_web_page_preview=True)