import os
import importlib
import asyncio
from pyrogram import idle, filters , Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery , Message
from Yumeko import app, log, scheduler
from config import config
from Yumeko.helper.on_start import edit_restart_message, clear_downloads_folder, notify_startup
from Yumeko.admin.roleassign import ensure_owner_is_hokage
from Yumeko.helper.state import initialize_services
from Yumeko.database import init_db
from asyncio import sleep
from Yumeko.decorator.save import save 
from Yumeko.decorator.errors import error 
import shutil
from Yumeko.modules.antiflood import cleanup_flood_tracker
import random
from pyrogram.errors import PeerIdInvalid
from Yumeko.helper.on_start import edit_restart_message, clear_downloads_folder, notify_startup, safe_send_message

async def safe_get_peer(app, peer_id):
    """
    Safely fetch a Telegram peer (user/group/channel).
    Returns the Chat object if found, else None.
    """
    try:
        peer = await app.get_chat(peer_id)  # fetch from Telegram if not in session
        return peer
    except PeerIdInvalid:
        log.warning(f"Invalid peer ID: {peer_id}")
    except Exception as e:
        log.warning(f"Failed to get peer {peer_id}: {e}")
    return None

MODULES = ["modules", "watchers", "admin", "decorator"]
LOADED_MODULES = {}


STICKER_FILE_ID = random.choices(
    config.START_STICKER_FILE_ID,
    weights=[1] * len(config.START_STICKER_FILE_ID)
)[0]


def cleanup():
    for root, dirs, _ in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                except Exception as e:
                    print(f"[bold yellow]Failed to delete {pycache_path}: {e}[/]")


# Load modules and extract __module__ and __help__
def load_modules_from_folder(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"Yumeko.{folder_name}.{module_name}")
            __module__ = getattr(module, "__module__", None)
            __help__ = getattr(module, "__help__", None)
            if __module__ and __help__:
                LOADED_MODULES[__module__] = __help__

def load_all_modules():
    for folder in MODULES:
        load_modules_from_folder(folder)
    log.info(f"Loaded {len(LOADED_MODULES)} modules: {', '.join(sorted(LOADED_MODULES.keys()))}")

# Pagination Logic
def get_paginated_buttons(page=1, items_per_page=15):
    modules = sorted(LOADED_MODULES.keys())
    total_pages = (len(modules) + items_per_page - 1) // items_per_page

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_modules = modules[start_idx:end_idx]

    buttons = [
        InlineKeyboardButton(mod, callback_data=f"help_{i}_{page}")
        for i, mod in enumerate(current_modules, start=start_idx)
    ]
    button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    # Navigation buttons logic
    if page == 1:  # First page: Next and Close vertically
        button_rows.append([
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])
    elif page == total_pages:  # Last page: Back and Close vertically
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])
    else:  # Other pages: Back, Close, Next horizontally
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}"),
            InlineKeyboardButton("🗑️", callback_data="delete"),
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}"),
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])

    return InlineKeyboardMarkup(button_rows)

# Helper to generate the main menu buttons
def get_main_menu_buttons():
    buttons = [
    [
        InlineKeyboardButton(
            "➕ 𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐆ʀᴏᴜᴘ",
            url=f"https://t.me/{app.me.username}?startgroup=true"
        )
    ],
    [
        InlineKeyboardButton("📞 𝐒ᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT_LINK),
        InlineKeyboardButton("🔔 𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/pookie_updates")
    ],
    [
        InlineKeyboardButton("👨‍💻 𝐂ᴏᴅᴇʀ", user_id=config.KHUSHI),
        InlineKeyboardButton("👑 𝐎ᴡɴᴇʀ", user_id=config.ZARYAB)
    ],
    [
        InlineKeyboardButton("📚 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="yumeko_help")
    ],
]

    return InlineKeyboardMarkup(buttons)

@app.on_callback_query(filters.regex("st_back"))
@error
async def start_lol(_, c : CallbackQuery):

    user_mention = c.from_user.mention(style="md")
    bot_mention = app.me.mention(style="md")
    await c.message.edit(
        text = f"**𝖧𝖾𝗒, {𝗎𝗌𝖾𝗋_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} 🧸**\n"
        f"**𝖨 𝖺𝗆 {𝖻𝗈𝗍_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} ♡ , 𝗒𝗈𝗎𝗋 𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗅𝖾 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖻𝗈𝗍, 𝖽𝖾𝗌𝗂𝗀𝗇𝖾𝖽 𝗍𝗈 𝗁𝖾𝗅𝗉 𝗒𝗈𝗎 𝗍𝖺𝗄𝖾 𝖼𝗈𝗇𝗍𝗋𝗈𝗅 𝗈𝖿 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝖾𝖺𝗌𝖾 𝗎𝗌𝗂𝗇𝗀 𝗆𝗒 𝗉𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝗆𝗈𝖽𝗎𝗅𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌!**\n\n"
        f"[✨]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖲𝖳𝖠𝖱𝖳_𝖨𝖬𝖦_𝖴𝖱𝖫}) **𝖶𝗁𝖺𝗍 𝖨 𝖢𝖺𝗇 𝖣𝗈:**\n"
        f" • 𝖲𝖾𝖺𝗆𝗅𝖾𝗌𝗌 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝗈𝖿 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌\n"
        f" • 𝖯𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝗍𝗈𝗈𝗅𝗌\n"
        f" • 𝖥𝗎𝗇 𝖺𝗇𝖽 𝖾𝗇𝗀𝖺𝗀𝗂𝗇𝗀 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌\n\n"
        f"📚 **𝖭𝖾𝖾𝖽 𝖧𝖾𝗅𝗉?**\n"
        f"𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖧𝖾𝗅𝗉 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖺𝗅𝗅 𝗍𝗁𝖾 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝖺𝖻𝗈𝗎𝗍 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.",
    reply_markup=get_main_menu_buttons()
    )


@app.on_callback_query(filters.regex("source_code"))
@error
async def source_code(_, clb: CallbackQuery):
    await clb.message.edit(
        text=(
            "✨ **Name:** Yumeko\n"
            "👨‍💻 **Developer:** [Aadiii](tg://user?id=5630057244)\n\n"
            "🤝 **Supporters:**\n"
            "   • [Eren Yeager](tg://user?id=2033411815)\n"
            "   • [ChatGPT](https://chatgpt.com)\n\n"
            "🤖 **Bots Under This Repository:**\n"
            "   • [Nezuko](https://t.me/NezukoProxBot)\n"
            "   • [Frieren](https://t.me/FrierenzBot)\n"
            "   • [Nobara](https://t.me/Nobara_Xprobot)\n"
            "   • [Arlecchino](https://t.me/ArlecchinoProxBot)\n"
            "   • [Kafka Honkai](https://t.me/Kafka_Xprobot)\n"
            "   • [Mikasa](https://t.me/Mikasa_Xprobot)\n\n"           
            "📂 **Source Code:** [Yumeko GitHub Repository](https://github.com/john-wick00/Yumekoo)"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
            ]
        ]),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("start" , config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def start_cmd(_, message : Message):

    # Check for parameters passed with the start command
    if len(message.command) > 1 and message.command[1] == "help":
        await help_command(Client, message)
        return

    #await message.react("🍓" , big = True)

    x = await message.reply_text(f"`ʜᴇʟʟᴏ {message.from_user.first_name} ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ \nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ. . . <3`")
    await sleep(0.4)
    await x.edit_text("🎊")
    await sleep(0.5)
    await x.edit_text("✨")
    await sleep(0.5)
    await x.edit_text("ꜱᴛᴀʀᴛɪɴɢ... ")
    await sleep(0.5)
    await x.delete()

    await message.reply_cached_media(file_id = STICKER_FILE_ID)    

    await sleep(0.2)

    user_mention = message.from_user.mention(style="md")
    bot_mention = app.me.mention(style="md")
    await message.reply(
        f"**𝖧𝖾𝗒, {𝗎𝗌𝖾𝗋_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} 🧸**\n"
        f"**𝖨 𝖺𝗆 {𝖻𝗈𝗍_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} , 𝗒𝗈𝗎𝗋 𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗅𝖾 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖻𝗈𝗍, 𝖽𝖾𝗌𝗂𝗀𝗇𝖾𝖽 𝗍𝗈 𝗁𝖾𝗅𝗉 𝗒𝗈𝗎 𝗍𝖺𝗄𝖾 𝖼𝗈𝗇𝗍𝗋𝗈𝗅 𝗈𝖿 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝖾𝖺𝗌𝖾 𝗎𝗌𝗂𝗇𝗀 𝗆𝗒 𝗉𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝗆𝗈𝖽𝗎𝗅𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌!**\n\n"
        f"[✨]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖲𝖳𝖠𝖱𝖳_𝖨𝖬𝖦_𝖴𝖱𝖫}) **𝖶𝗁𝖺𝗍 𝖨 𝖢𝖺𝗇 𝖣𝗈:**\n"
        f" • 𝖲𝖾𝖺𝗆𝗅𝖾𝗌𝗌 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝗈𝖿 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌\n"
        f" • 𝖯𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝗍𝗈𝗈𝗅𝗌\n"
        f" • 𝖥𝗎𝗇 𝖺𝗇𝖽 𝖾𝗇𝗀𝖺𝗀𝗂𝗇𝗀 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌\n\n"
        f"📚 **𝖭𝖾𝖾𝖽 𝖧𝖾𝗅𝗉?**\n"
        f"𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖧𝖾𝗅𝗉 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖺𝗅𝗅 𝗍𝗁𝖾 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝖺𝖻𝗈𝗎𝗍 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.",
    reply_markup=get_main_menu_buttons()
    )


@app.on_message(filters.command("help", prefixes=config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def help_command(client, message: Message):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await message.reply(
        text=f"**𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝖺𝗅𝗅 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌!**\n"
             f"**𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝖺 𝗆𝗈𝖽𝗎𝗅𝖾 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖽𝖾𝗍𝖺𝗂𝗅𝖾𝖽 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖺𝖻𝗈𝗎𝗍 𝗂𝗍.**\n\n"
             f"🔹 **𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖯𝗋𝖾𝖿𝗂𝗑𝖾𝗌:** {prefixes} \n\n"
             f"[📩]({config.HELP_IMG_URL}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"𝖱𝖾𝗉𝗈𝗋𝗍 𝗂𝗍 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 /𝖻𝗎𝗀 𝖼𝗈𝗆𝗆𝖺𝗇𝖽, 𝖺𝗇𝖽 𝖨’𝗅𝗅 𝗀𝖾𝗍 𝗂𝗍 𝖿𝗂𝗑𝖾𝖽 𝖺𝗌 𝗌𝗈𝗈𝗇 𝖺𝗌 𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾!",
    reply_markup=get_paginated_buttons()
    )

@app.on_callback_query(filters.regex(r"^yumeko_help$"))
async def show_help_menu(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await query.message.edit(
        𝗍𝖾𝗑𝗍=f"**𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝖺𝗅𝗅 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌!**\n"
             f"**𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝖺 𝗆𝗈𝖽𝗎𝗅𝖾 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖽𝖾𝗍𝖺𝗂𝗅𝖾𝖽 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖺𝖻𝗈𝗎𝗍 𝗂𝗍.**\n\n"
             f"🔹 **𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖯𝗋𝖾𝖿𝗂𝗑𝖾𝗌:** {𝗉𝗋𝖾𝖿𝗂𝗑𝖾𝗌} \n\n"
             f"[📩]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖧𝖤𝖫𝖯_𝖨𝖬𝖦_𝖴𝖱𝖫}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"𝖱𝖾𝗉𝗈𝗋𝗍 𝗂𝗍 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 /𝖻𝗎𝗀 𝖼𝗈𝗆𝗆𝖺𝗇𝖽, 𝖺𝗇𝖽 𝖨’𝗅𝗅 𝗀𝖾𝗍 𝗂𝗍 𝖿𝗂𝗑𝖾𝖽 𝖺𝗌 𝗌𝗈𝗈𝗇 𝖺𝗌 𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾!",
    reply_markup=get_paginated_buttons()
    )

# Callback query handler for module help
@app.on_callback_query(filters.regex(r"^help_\d+_\d+$"))
async def handle_help_callback(client, query: CallbackQuery):
    data = query.data
    try:
        # Extract the numeric index and page from the callback data
        parts = data.split("_")
        module_index = int(parts[1])
        current_page = int(parts[2])

        modules = sorted(LOADED_MODULES.keys())

        # Retrieve the module name using the index
        module_name = modules[module_index]
        help_text = LOADED_MODULES.get(module_name, "No help available for this module.")

        # Edit the message to display the help text
        await query.message.edit(
            text=f"{help_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data=f"area_{current_page}")]
            ])
        )
    except (ValueError, IndexError) as e:
        await query.answer("Invalid module selected. Please try again.")

# Callback query handler for pagination
@app.on_callback_query(filters.regex(r"^area_\d+$"))
async def handle_pagination_callback(client, query: CallbackQuery):
    data = query.data
    try:
        page = int(data[5:])
        prefixes = " ".join(config.COMMAND_PREFIXES)

        # Edit both the message text and reply markup
        await query.message.edit(
        𝗍𝖾𝗑𝗍=f"**𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝖺𝗅𝗅 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌!**\n"
             f"**𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝖺 𝗆𝗈𝖽𝗎𝗅𝖾 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖽𝖾𝗍𝖺𝗂𝗅𝖾𝖽 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖺𝖻𝗈𝗎𝗍 𝗂𝗍.**\n\n"
             f"🔹 **𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖯𝗋𝖾𝖿𝗂𝗑𝖾𝗌:** {𝗉𝗋𝖾𝖿𝗂𝗑𝖾𝗌} \n\n"
             f"[📩]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖧𝖤𝖫𝖯_𝖨𝖬𝖦_𝖴𝖱𝖫}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"𝖱𝖾𝗉𝗈𝗋𝗍 𝗂𝗍 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 /𝖻𝗎𝗀 𝖼𝗈𝗆𝗆𝖺𝗇𝖽, 𝖺𝗇𝖽 𝖨’𝗅𝗅 𝗀𝖾𝗍 𝗂𝗍 𝖿𝗂𝗑𝖾𝖽 𝖺𝗌 𝗌𝗈𝗈𝗇 𝖺𝗌 𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾!",
            reply_markup=get_paginated_buttons(page)
        )
    except Exception as e:
        await query.answer("Error occurred while navigating pages. Please try again.")

# Callback query handler for main menu
@app.on_callback_query(filters.regex(r"^main_menu$"))
async def handle_main_menu_callback(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)

    await query.message.edit(
        𝗍𝖾𝗑𝗍=f"**𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝖺𝗅𝗅 𝗆𝗒 𝗆𝗈𝖽𝗎𝗅𝖾𝗌!**\n"
             f"**𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝖺 𝗆𝗈𝖽𝗎𝗅𝖾 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖽𝖾𝗍𝖺𝗂𝗅𝖾𝖽 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖺𝖻𝗈𝗎𝗍 𝗂𝗍.**\n\n"
             f"🔹 **𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖯𝗋𝖾𝖿𝗂𝗑𝖾𝗌:** {𝗉𝗋𝖾𝖿𝗂𝗑𝖾𝗌} \n\n"
             f"[📩]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖧𝖤𝖫𝖯_𝖨𝖬𝖦_𝖴𝖱𝖫}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"𝖱𝖾𝗉𝗈𝗋𝗍 𝗂𝗍 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 /𝖻𝗎𝗀 𝖼𝗈𝗆𝗆𝖺𝗇𝖽, 𝖺𝗇𝖽 𝖨’𝗅𝗅 𝗀𝖾𝗍 𝗂𝗍 𝖿𝗂𝗑𝖾𝖽 𝖺𝗌 𝗌𝗈𝗈𝗇 𝖺𝗌 𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾!",
    reply_markup=get_paginated_buttons()
    )

@app.on_message(filters.command(["start" , "help"], prefixes=config.COMMAND_PREFIXES) & filters.group)
async def start_command(client, message: Message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sᴛᴀʀᴛ ɪɴ ᴘᴍ", url="https://t.me/kafka_xprobt?start=help")]
    ])
    await message.reply(
        text=f"**𝖧𝖾𝗅𝗅𝗈, {message.from_user.first_name} <3**\n"
             f"𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝖾𝗑𝗉𝗅𝗈𝗋𝖾 𝗆𝗒 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌!",
        reply_markup=button
    )



if __name__ == "__main__":
    load_all_modules()

    try:
        app.start()
        initialize_services()
        ensure_owner_is_hokage()
        edit_restart_message()
        clear_downloads_folder()
        notify_startup()

        loop = asyncio.get_event_loop()

        async def initialize_async_components():

            await init_db()
            scheduler.start()

            # Schedule the antiflood cleanup task to run every 5 minutes
            scheduler.add_job(cleanup_flood_tracker, 'interval', minutes=5, id='antiflood_cleanup')
            log.info("Scheduled antiflood cleanup task to run every 5 minutes")

            log.info("Async components initialized.")

            bot_details = await app.get_me()
            log.info(f"Bot Configured: Name: {bot_details.first_name}, ID: {bot_details.id}, Username: @{bot_details.username}")

        loop.run_until_complete(initialize_async_components())
        log.info("Bot started. Press Ctrl+C to stop.")
        idle()

        cleanup()

        app.stop()

    except Exception as e:
        log.exception(e)
