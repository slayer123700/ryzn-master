from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import random
from Yumeko import app
from Yumeko.vars import FLIRT as FLIRT_STRINGS , TOSS as TOSS_STRINGS , EYES , MOUTHS , EARS , DECIDE as DECIDE_STRINGS , weebyfont , normiefont 
from config import config
from pyrogram.enums import ParseMode
from Yumeko.decorator.save import save 
from Yumeko.decorator.errors import error


async def fetch_from_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

@app.on_message(filters.command("pickwinner" , config.COMMAND_PREFIXES))
@error
@save
async def pick_winner(client: Client, message: Message):
    participants = message.text.split()[1:]
    if participants:
        winner = random.choice(participants)
        await message.reply_text(f"\ud83c\udf89 𝖳𝗁𝖾 𝗐𝗂𝗇𝗇𝖾𝗋 𝗂𝗌: {winner}")
    else:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗅𝗂𝗌𝗍 𝗈𝖿 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝗌.")

@app.on_message(filters.command("hyperlink" , config.COMMAND_PREFIXES))
@error
@save
async def hyperlink_command(client: Client, message: Message):
    args = message.text.split()[1:]
    if len(args) >= 2:
        text = " ".join(args[:-1])
        link = args[-1]
        hyperlink = f"[{text}]({link})"
        await message.reply_text(hyperlink, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply_text("𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖿𝗈𝗋𝗆𝖺𝗍! 𝖴𝗌𝖾: /𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄 <𝗍𝖾𝗑𝗍> <𝗅𝗂𝗇𝗄>")

@app.on_message(filters.command("joke" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"(?i)^Yumeko Ek Joke Sunao$"))
@error
@save
async def joke(client: Client, message: Message):
    joke = await fetch_from_api("https://official-joke-api.appspot.com/random_joke")
    await message.reply_text(f"{joke['setup']} - {joke['punchline']}")

@app.on_message(filters.command("truth" , config.COMMAND_PREFIXES))
@error
@save
async def truth(client: Client, message: Message):
    truth_question = await fetch_from_api("https://api.truthordarebot.xyz/v1/truth")
    await message.reply_text(truth_question["question"])

@app.on_message(filters.command("dare" , config.COMMAND_PREFIXES))
@error
@save
async def dare(client: Client, message: Message):
    dare_question = await fetch_from_api("https://api.truthordarebot.xyz/v1/dare")
    await message.reply_text(dare_question["question"])

@app.on_message(filters.command("roll" , config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def roll(client: Client, message: Message):
    await message.reply_text(random.randint(1, 6))

@app.on_message(filters.command("flirt" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"(?i)^Yumeko flirt$"))
@error
@save
async def flirt(client: Client, message: Message):
    await message.reply_text(random.choice(FLIRT_STRINGS))

@app.on_message(filters.command("toss" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"(?i)^Yumeko toss$"))
@error
@save
async def toss(client: Client, message: Message):
    await message.reply_text(random.choice(TOSS_STRINGS))

@app.on_message(filters.command("shrug" , config.COMMAND_PREFIXES))
@error
@save
async def shrug(client: Client, message: Message):
    await message.reply_text(r"¯\_(ツ)_/¯")

@app.on_message(filters.command("bluetext" , config.COMMAND_PREFIXES))
@error
@save
async def bluetext(client: Client, message: Message):
    await message.reply_text("/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS")

@app.on_message(filters.command("rlg" , config.COMMAND_PREFIXES))
@error
@save
async def rlg(client: Client, message: Message):
    eyes = random.choice(EYES)
    mouth = random.choice(MOUTHS)
    ears = random.choice(EARS)
    face = f"{ears[0]}{eyes}{mouth}{eyes}{ears[1]}"
    await message.reply_text(face)

@app.on_message(filters.command("decide" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"(?i)^Yumeko decide$"))
@error
@save
async def decide(client: Client, message: Message):
    await message.reply_text(random.choice(DECIDE_STRINGS))

@app.on_message(filters.command("weebify" , config.COMMAND_PREFIXES))
@error
@save
async def webify(client: Client, message: Message):
    args = message.command[1:]  # Extract arguments from the command
    string = ""

    if message.reply_to_message and message.reply_to_message.text:
        string = message.reply_to_message.text.lower().replace(" ", "  ")

    if args:
        string = "  ".join(args).lower()

    if not string:
        await message.reply_text(
            "𝖴𝗌𝖺𝗀𝖾: `/𝗐𝖾𝖾𝖻𝗂𝖿𝗒 <𝗍𝖾𝗑𝗍>`",
        )
        return

    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)

    if message.reply_to_message:
        await message.reply_to_message.reply_text(string)
    else:
        await message.reply_text(string)
