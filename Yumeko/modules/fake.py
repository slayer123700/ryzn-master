from faker import Faker
from faker.providers import internet
from pyrogram import filters
from pyrogram.types import Message

from Yumeko import app

fake = Faker()
fake.add_provider(internet)

__module__ = "Fake Info"

__help__ = """
**Fake info generator**

**Commands**

♠ `/fakegen` : Generates Fake Information (PM only)
♠ `/picgen` : Generate a Fake pic (PM only)
"""

# ----------------- FAKE INFO -----------------
@app.on_message(filters.command("fakegen") & filters.private)
async def fakegen(_, message: Message):
    name = fake.name()
    address = fake.address()
    ip = fake.ipv4_private()
    cc = fake.credit_card_full()
    email = fake.ascii_free_email()
    job = fake.job()
    android = fake.android_platform_token()
    pc = fake.chrome()

    text = (
        f"**🛡 Fake Information Generated**\n\n"
        f"**Name:** `{name}`\n"
        f"**Address:** `{address}`\n"
        f"**IP Address:** `{ip}`\n"
        f"**Credit Card:** `{cc}`\n"
        f"**Email:** `{email}`\n"
        f"**Job:** `{job}`\n"
        f"**Android User-Agent:** `{android}`\n"
        f"**PC User-Agent:** `{pc}`\n\n"
        f"⚠️ This message will be deleted in 30 seconds."
    )

    msg = await message.reply_text(text)
    await asyncio.sleep(30)
    await msg.delete()
    await message.delete()

# --------------- FAKE PIC -------------------
@app.on_message(filters.command("picgen") & filters.private)
async def picgen(_, message: Message):
    img_url = "https://thispersondoesnotexist.com/image"
    text = "🖼 Fake Image successfully generated.\n\n⚠️ This message will be deleted in 30 seconds."

    msg = await message.reply_photo(photo=img_url, caption=text)
    await asyncio.sleep(30)
    await msg.delete()
    await message.delete()

# --------------- PRIVATE ONLY NOTIFY ----------
@app.on_message(filters.command(["fakegen", "picgen"]) & ~filters.private)
async def fake_pm_only(_, message: Message):
    warn = await message.reply_text("⚠️ This command can only be used in PM with the bot!")
    await asyncio.sleep(5)
    await warn.delete()