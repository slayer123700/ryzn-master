
import os
import importlib
import asyncio
import shutil
from asyncio import sleep
from pyrogram import idle, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from Yumeko import app, log, scheduler
from config import config
from Yumeko.helper.on_start import edit_restart_message, clear_downloads_folder, notify_startup
from Yumeko.admin.roleassign import ensure_owner_is_hokage
from Yumeko.helper.state import initialize_services
from Yumeko.database import init_db
from Yumeko.decorator.save import save
from Yumeko.decorator.errors import error


MODULES = ["modules", "watchers", "admin", "decorator"]
LOADED_MODULES = {}

STICKER_FILE_ID = random.choice(config.START_STICKER_FILE_ID)

# SMALL CAPS CONVERSION MAP (Unicode)
SMALL_CAPS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)

def to_small_caps(text):
    """Convert text to elegant small caps"""
    return text.translate(SMALL_CAPS)

def cleanup():
    for root, dirs, _ in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                except Exception as e:
                    log.warning(f"Failed to delete {pycache_path}: {e}")

def load_modules_from_folder(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"Yumeko.{folder_name}.{module_name}")
                __module__ = getattr(module, "__module__", None)
                __help__ = getattr(module, "__help__", None)
                if __module__ and __help__:
                    LOADED_MODULES[__module__] = __help__
            except Exception as e:
                log.error(f"Failed to load module {module_name}: {e}")

def load_all_modules():
    for folder in MODULES:
        load_modules_from_folder(folder)
    log.info(f"Loaded {len(LOADED_MODULES)} modules: {', '.join(sorted(LOADED_MODULES.keys()))}")

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

    button_rows.append([
        InlineKeyboardButton(
            "❮",
            callback_data=f"area_{page - 1}" if page > 1 else "noop"
        ),
        InlineKeyboardButton(
            "⚔️ ᴄʟᴏꜱᴇ",
            callback_data="delete"
        ),
        InlineKeyboardButton(
            "❯",
            callback_data=f"area_{page + 1}" if page < total_pages else "noop"
        ),
    ])

    button_rows.append([
        InlineKeyboardButton("🔙 ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="st_back")
    ])

    return InlineKeyboardMarkup(button_rows)

def get_main_menu_buttons():
    # FIXED: Removed double spaces in URL
    invite_link = f"https://t.me/{app.me.username}?startgroup=true"
    
    buttons = [
        [
            InlineKeyboardButton(
                "⚡ ᴅᴇᴘʟᴏʏ ᴛᴏ ɢʀᴏᴜᴘ",
                url=invite_link
            )
        ],
        [
            InlineKeyboardButton("🛡️ ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT_LINK),
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", user_id=config.OWNER_ID)
        ],
        [
            InlineKeyboardButton("📜 ᴄᴏᴍᴍᴀɴᴅ ᴀʀꜱᴇɴᴀʟ", callback_data="yumeko_help"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# =============== ESSENTIAL HANDLERS (PREVENT "UNKNOWN ACTION" ERRORS) ===============
@app.on_callback_query()
async def auto_answer_all(client, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass
@app.on_callback_query(filters.regex("^noop$"))
async def noop_handler(_, query: CallbackQuery):
    await query.answer(
        to_small_caps("ʙᴏᴜɴᴅᴀʀʏ ʀᴇᴀᴄʜᴇᴅ • ɴᴏ ꜰᴜʀᴛʜᴇʀ ᴘᴀɢᴇꜱ"),
        show_alert=False
    )


@app.on_callback_query(filters.regex("^delete$"))
async def delete_handler(_, query: CallbackQuery):
    try:
        await query.message.delete()
        await query.answer(
            to_small_caps("ɪɴᴛᴇʀꜰᴀᴄᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ"),
            show_alert=False
        )
    except Exception:
        await query.answer()


@app.on_callback_query(filters.regex("^st_back$"))
@error
async def start_lol(_, c: CallbackQuery):
    await c.answer()

    user_name = c.from_user.first_name
    bot_name = app.me.first_name

    # continue your existing logic here

    # FIXED: Proper indentation and variable naming
    text = (
        "𝗛𝗲𝘆, ㅤㅤ ⚡\n"
        f"𝗜 𝗮𝗺 {bot_name} ♡, 𝘆𝗼𝘂𝗿 𝘃𝗲𝗿𝘀𝗮𝘁𝗶𝗹𝗲 𝘁𝗮𝗰𝘁𝗶𝗰𝗮𝗹 𝗺𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗯𝗼𝘁, 𝗱𝗲𝘀𝗶𝗴𝗻𝗲𝗱 𝘁𝗼 𝗵𝗲𝗹𝗽 𝘆𝗼𝘂 𝘁𝗮𝗸𝗲 𝗼𝘃𝗲𝗿 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽𝘀 𝘄𝗶𝘁𝗵 𝗲𝗮𝘀𝗲 𝘂𝘀𝗶𝗻𝗴 𝗺𝘆 𝗽𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗺𝗼𝗱𝘂𝗹𝗲𝘀 𝗮𝗻𝗱 𝘀𝘁𝗿𝗶𝗸𝗶𝗻𝗴 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀!\n"
        ">\n"
        "> • 𝗦𝗲𝗮𝗺𝗹𝗲𝘀𝘀 𝗺𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗼𝗳 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽𝘀 🚀\n"
        "> • 𝗣𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗶𝗼𝗻 𝘁𝗼𝗼𝗹𝘀 🛡️\n"
        "> • 𝗙𝘂𝗻 𝗮𝗻𝗱 𝗲𝗻𝗴𝗮𝗴𝗶𝗻𝗴 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀 🎮\n"
        ">\n"
        "✧ 𝗧𝗔𝗖𝗧𝗜𝗖𝗔𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗨𝗡𝗜𝗧 ✧ 🛡️ ║ ▸ READY\n"
        f"> 🤖 {bot_name} ▸ ACTIVE\n"
        ">\n"
        "> \"𝗗𝗶𝘀𝗰𝗶𝗽𝗹𝗶𝗻𝗲 𝗙𝗼𝗿𝗴𝗲𝘀 𝘄𝗮𝗿𝗿𝗶𝗼𝗿𝘀.\" ⚔️\n"
        "> — 𝗠𝘂𝘀𝗮𝘀𝗵𝗶 ✦\n"
        ">\n"
        "📚 𝗡𝗲𝗲𝗱 𝗛𝗲𝗹𝗽?\n"
        "𝗖𝗹𝗶𝗰𝗸 𝘁𝗵𝗲 𝗛𝗲𝗹𝗽 𝗯𝘂𝘁𝘁𝗼𝗻 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 𝗮𝗻𝗱 𝘁𝘂𝘁𝗼𝗿𝗶𝗮𝗹𝘀 𝗮𝗻𝗱 𝗴𝘂𝗶𝗱𝗲𝘀 ✨\n"
        "✧ ᴇɴᴅ ᴏꜰ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ✧ 🌌 ║ ⬢"
    )
    
    # FIXED: Use edit_caption for media messages (keeps photo intact)
    await c.message.edit_caption(
        caption=text,
        reply_markup=get_main_menu_buttons(),
    )

@app.on_callback_query(filters.regex("^source_code$"))
@error
async def source_code(_, clb: CallbackQuery):
    await clb.answer()
    # FIXED: Proper indentation and variable naming
    text = (
        "> ✧ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗦𝗬𝗦𝗧𝗘𝗠 ✧\n"
        ">\n"
        "> \"𝗖𝗢𝗗𝗘 𝗜𝗦 𝗟𝗜𝗞𝗘 𝗛𝗨𝗠𝗢𝗥\\. 𝗪𝗛𝗘𝗡 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗧𝗢 𝗘𝗫𝗣𝗟𝗔𝗜𝗡 𝗜𝗧, 𝗜𝗧'𝗦 𝗕𝗔𝗗\\.\n"
        "> — 𝗖𝗢𝗥𝗬 𝗛𝗢𝗨𝗦𝗘\n"
        ">\n"
        "> ✧ 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 𝗦𝗧𝗔𝗧𝗨𝗦 ✧\n"
        "> • 𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗖𝗖𝗘𝗦𝗦: 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗧𝗘𝗗\n"
        "> • 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗔𝗧𝗜𝗢𝗡: 𝗢𝗪𝗡𝗘𝗥\\-𝗢𝗡𝗟𝗬\n"
        ">\n"
        "> ✧ 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥 𝗙𝗢𝗥 𝗔𝗖𝗖𝗘𝗦𝗦 ✧"
    )
    
    # FIXED: Use edit_caption for media messages
    await clb.message.edit_caption(
        caption=text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʀᴇᴛᴜʀɴ ᴛᴏ ᴄᴏᴍᴍᴀɴᴅ", callback_data="st_back")]
        ])
    )

@app.on_message(filters.command("start", config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def start_cmd(_, message: Message):
    if len(message.command) > 1 and message.command[1] == "help":
        await help_command(_, message)
        return
    
    await message.react("⚡", big=True)
    
    x = await message.reply_text(f"`{to_small_caps('ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ꜱʏꜱᴛᴇᴍꜱ...')}`")
    await sleep(0.4)
    await x.edit_text(f"`{to_small_caps('> ꜱʏꜱᴛᴇᴍꜱ ᴏɴʟɪɴᴇ')}`")
    await sleep(0.4)
    await x.delete()
    
    await message.reply_cached_media(file_id=STICKER_FILE_ID)
    await sleep(0.3)
    
    user_name = message.from_user.first_name
    bot_name = app.me.first_name
    
    # FIXED: Proper variable naming
    caption = (
        "𝗛𝗲𝘆, ㅤㅤ ⚡\n"
        f"𝗜 𝗮𝗺 {bot_name} ♡, 𝘆𝗼𝘂𝗿 𝘃𝗲𝗿𝘀𝗮𝘁𝗶𝗹𝗲 𝘁𝗮𝗰𝘁𝗶𝗰𝗮𝗹 𝗺𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗯𝗼𝘁, 𝗱𝗲𝘀𝗶𝗴𝗻𝗲𝗱 𝘁𝗼 𝗵𝗲𝗹𝗽 𝘆𝗼𝘂 𝘁𝗮𝗸𝗲 𝗼𝘃𝗲𝗿 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽𝘀 𝘄𝗶𝘁𝗵 𝗲𝗮𝘀𝗲 𝘂𝘀𝗶𝗻𝗴 𝗺𝘆 𝗽𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗺𝗼𝗱𝘂𝗹𝗲𝘀 𝗮𝗻𝗱 𝘀𝘁𝗿𝗶𝗸𝗶𝗻𝗴 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀!\n"
        ">\n"
        "> • 𝗦𝗲𝗮𝗺𝗹𝗲𝘀𝘀 𝗺𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗼𝗳 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽𝘀 🚀\n"
        "> • 𝗣𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗶𝗼𝗻 𝘁𝗼𝗼𝗹𝘀 🛡️\n"
        "> • 𝗙𝘂𝗻 𝗮𝗻𝗱 𝗲𝗻𝗴𝗮𝗴𝗶𝗻𝗴 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀 🎮\n"
        ">\n"
        "✧ 𝗧𝗔𝗖𝗧𝗜𝗖𝗔𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗨𝗡𝗜𝗧 ✧ 🛡️ ║ ▸ READY\n"
        f"> 🤖 {bot_name} ▸ ACTIVE\n"
        ">\n"
        "> \"𝗗𝗶𝘀𝗰𝗶𝗽𝗹𝗶𝗻𝗲 𝗙𝗼𝗿𝗴𝗲𝘀 𝘄𝗮𝗿𝗿𝗶𝗼𝗿𝘀.\" ⚔️\n"
        "> — 𝗠𝘂𝘀𝗮𝘀𝗵𝗶 ✦\n"
        ">\n"
        "📚 𝗡𝗲𝗲𝗱 𝗛𝗲𝗹𝗽?\n"
        "𝗖𝗹𝗶𝗰𝗸 𝘁𝗵𝗲 𝗛𝗲𝗹𝗽 𝗯𝘂𝘁𝘁𝗼𝗻 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 𝗮𝗻𝗱 𝘁𝘂𝘁𝗼𝗿𝗶𝗮𝗹𝘀 𝗮𝗻𝗱 𝗴𝘂𝗶𝗱𝗲𝘀 ✨\n"
        "✧ ᴇɴᴅ ᴏꜰ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ✧ 🌌 ║ ⬢"
    )
    
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=caption,
        reply_markup=get_main_menu_buttons(),
        message_effect_id=5159385139981059251
    )

@app.on_message(filters.command("help", prefixes=config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def help_command(_, message: Message):
    prefixes = " | ".join(config.COMMAND_PREFIXES)
    small_caps_prefixes = to_small_caps(prefixes)
    
    caption = (
        "> ✧ 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 ✧\n"
        ">\n"
        "> \"𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘 𝐖𝐈𝐓𝐇𝐎𝐔𝐓 𝐓𝐀𝐂𝐓𝐈𝐂𝐒 𝐈𝐒 𝐓𝐇𝐄 𝐒𝐋𝐎𝐖𝐄𝐒𝐓 𝐑𝐎𝐔𝐓𝐄 𝐓𝐎 𝐕𝐈𝐂𝐓𝐎𝐑𝐘\\.\n"
        "> — 𝐒𝐔𝐍 𝐓𝐙𝐔\n"
        ">\n"
        "> ✧ 𝐒𝐄𝐋𝐄𝐂𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐅𝐎𝐑 𝐒𝐏𝐄𝐂𝐒 ✧\n"
        f"> 𝐏𝐑𝐄𝐅𝐈𝐗𝐄𝐒: {small_caps_prefixes}\n"
        ">\n"
        "> ✧ 𝐓𝐇𝐑𝐄𝐀𝐓 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 ✧\n"
        "> 𝐃𝐄𝐏𝐋𝐎𝐘 /𝐁𝐔𝐆 𝐅𝐎𝐑 𝐂𝐑𝐈𝐓𝐈𝐂𝐀𝐋 𝐀𝐋𝐄𝐑𝐓𝐒"
    )
    
    await message.reply_photo(
        photo=config.HELP_IMG_URL,
        caption=caption,
        reply_markup=get_paginated_buttons()
    )

@app.on_callback_query(filters.regex(r"^yumeko_help$"))
async def show_help_menu(_, query: CallbackQuery):
    await query.answer()
    prefixes = " | ".join(config.COMMAND_PREFIXES)
    small_caps_prefixes = to_small_caps(prefixes)
    
    caption = (
        "> ✧ 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 ✧\n"
        ">\n"
        "> \"𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘 𝐖𝐈𝐓𝐇𝐎𝐔𝐓 𝐓𝐀𝐂𝐓𝐈𝐂𝐒 𝐈𝐒 𝐓𝐇𝐄 𝐒𝐋𝐎𝐖𝐄𝐒𝐓 𝐑𝐎𝐔𝐓𝐄 𝐓𝐎 𝐕𝐈𝐂𝐓𝐎𝐑𝐘\\.\n"
        "> — 𝐒𝐔𝐍 𝐓𝐙𝐔\n"
        ">\n"
        "> ✧ 𝐒𝐄𝐋𝐄𝐂𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐅𝐎𝐑 𝐒𝐏𝐄𝐂𝐒 ✧\n"
        f"> 𝐏𝐑𝐄𝐅𝐈𝐗𝐄𝐒: {small_caps_prefixes}\n"
        ">\n"
        "> ✧ 𝐓𝐇𝐑𝐄𝐀𝐓 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 ✧\n"
        "> 𝐃𝐄𝐏𝐋𝐎𝐘 /𝐁𝐔𝐆 𝐅𝐎𝐑 𝐂𝐑𝐈𝐓𝐈𝐂𝐀𝐋 𝐀𝐋𝐄𝐑𝐓𝐒"
    )
    
    # FIXED: Use edit_caption for media messages
    await query.message.edit_caption(
        caption=caption,
        reply_markup=get_paginated_buttons()
    )

@app.on_callback_query(filters.regex(r"^help_(\d+)_(\d+)$"))
async def handle_help_callback(_, query: CallbackQuery):
    await query.answer()
    match = query.matches[0]
    module_index = int(match.group(1))
    current_page = int(match.group(2))

    modules = sorted(LOADED_MODULES.keys())
    if module_index >= len(modules):
        await query.answer(to_small_caps("ᴍᴏᴅᴜʟᴇ ᴏꜰꜰʟɪɴᴇ • ʀᴇɪɴɪᴛɪᴀʟɪᴢɪɴɢ ꜱʏꜱᴛᴇᴍꜱ"), show_alert=True)
        return
        
    module_name = modules[module_index]
    help_text = LOADED_MODULES.get(module_name, "ᴛᴀᴄᴛɪᴄᴀʟ ᴅᴀᴛᴀ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴛʜɪꜱ ᴍᴏᴅᴜʟᴇ.")
    small_caps_help = to_small_caps(help_text)
    small_caps_module = to_small_caps(module_name.replace('_', ' • '))
    
    text = (
        f"> ✧ {small_caps_module.upper()} ✧\n"
        ">\n"
        f"> {small_caps_help.upper()}\n"
        ">\n"
        "> ✧ 𝐄𝐍𝐃 𝐎𝐅 𝐓𝐑𝐀𝐍𝐒𝐌𝐈𝐒𝐒𝐈𝐎𝐍 ✧"
    )
    
    # FIXED: Use edit_caption for media messages (keeps photo)
    await query.message.edit_caption(
        caption=text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʀᴇᴛᴜʀɴ ᴛᴏ ᴀʀꜱᴇɴᴀʟ", callback_data=f"area_{current_page}")]
        ])
    )

@app.on_callback_query(filters.regex(r"^area_(\d+)$"))
async def handle_pagination_callback(_, query: CallbackQuery):
    await query.answer()
    page = int(query.matches[0].group(1))
    prefixes = " | ".join(config.COMMAND_PREFIXES)
    small_caps_prefixes = to_small_caps(prefixes)
    
    modules = sorted(LOADED_MODULES.keys())
    total_pages = (len(modules) + 14) // 15
    if page < 1 or page > total_pages:
        await query.answer(to_small_caps("ɪɴᴠᴀʟɪᴅ ᴄᴏᴏʀᴅɪɴᴀᴛᴇꜱ • ʀᴇᴅɪʀᴇᴄᴛɪɴɢ ᴛᴏ ᴍᴀɪɴ ᴀʀꜱᴇɴᴀʟ"), show_alert=True)
        page = 1

    caption = (
        "> ✧ 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 ✧\n"
        ">\n"
        "> \"𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘 𝐖𝐈𝐓𝐇𝐎𝐔𝐓 𝐓𝐀𝐂𝐓𝐈𝐂𝐒 𝐈𝐒 𝐓𝐇𝐄 𝐒𝐋𝐎𝐖𝐄𝐒𝐓 𝐑𝐎𝐔𝐓𝐄 𝐓𝐎 𝐕𝐈𝐂𝐓𝐎𝐑𝐘\\.\n"
        "> — 𝐒𝐔𝐍 𝐓𝐙𝐔\n"
        ">\n"
        "> ✧ 𝐒𝐄𝐋𝐄𝐂𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐅𝐎𝐑 𝐒𝐏𝐄𝐂𝐒 ✧\n"
        f"> 𝐏𝐑𝐄𝐅𝐈𝐗𝐄𝐒: {small_caps_prefixes}\n"
        ">\n"
        "> ✧ 𝐓𝐇𝐑𝐄𝐀𝐓 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 ✧\n"
        "> 𝐃𝐄𝐏𝐋𝐎𝐘 /𝐁𝐔𝐆 𝐅𝐎𝐑 𝐂𝐑𝐈𝐓𝐈𝐂𝐀𝐋 𝐀𝐋𝐄𝐑𝐓𝐒"
    )

    # FIXED: Use edit_caption for media messages
    await query.message.edit_caption(
        caption=caption,
        reply_markup=get_paginated_buttons(page)
    )

@app.on_message(filters.command(["start", "help"], prefixes=config.COMMAND_PREFIXES) & filters.group)
async def start_command(_, message: Message):
    # FIXED: Removed double spaces in URL
    pm_link = f"https://t.me/{app.me.username}?start=help"
    
    text = (
        "> ✧ 𝐒𝐄𝐂𝐔𝐑𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 ✧\n"
        ">\n"
        f"> {message.from_user.first_name.upper()}\n"
        ">\n"
        "> \"𝐇𝐄 𝐖𝐇𝐎 𝐃𝐄𝐅𝐄𝐍𝐃𝐒 𝐄𝐕𝐄𝐑𝐘𝐓𝐇𝐈𝐍𝐆 𝐃𝐄𝐅𝐄𝐍𝐃𝐒 𝐍𝐎𝐓𝐇𝐈𝐍𝐆\\.\n"
        "> — 𝐅𝐑𝐄𝐃𝐄𝐑𝐈𝐂𝐊 𝐓𝐇𝐄 𝐆𝐑𝐄𝐀𝐓\n"
        ">\n"
        "> ✧ 𝐖𝐀𝐑𝐍𝐈𝐍𝐆 ✧\n"
        "> 𝐅𝐔𝐋𝐋 𝐓𝐀𝐂𝐓𝐈𝐂𝐀𝐋 𝐈𝐍𝐓𝐄𝐑𝐅𝐀𝐂𝐄 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐒 𝐏𝐑𝐈𝐕𝐀𝐓𝐄 𝐒𝐄𝐒𝐒𝐈𝐎𝐍"
    )
    
    await message.reply(
        text=text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 ᴏᴘᴇɴ ꜱᴇᴄᴜʀᴇ ꜱᴇꜱꜱɪᴏɴ", url=pm_link)]
        ])
    )

# =============== CATCH-ALL HANDLER (PREVENTS UNKNOWN ACTION FLOODS) ===============

@app.on_callback_query(filters.regex("^(?!help_|area_|yumeko_help$|st_back$|delete$|noop$|source_code$).*"))
async def fallback_handler(_, query: CallbackQuery):
    await query.answer(
        to_small_caps("⚠️ ᴄᴏᴍᴍᴀɴᴅ ᴇxᴘɪʀᴇᴅ • ʀᴇꜱᴛᴀʀᴛ ɪɴᴛᴇʀᴀᴄᴛɪᴏɴ"),
        show_alert=True
    )
    log.warning(f"Unhandled callback: {query.data} from {query.from_user.id}")


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
            log.info(to_small_caps("ᴀꜱʏɴᴄ ꜱʏꜱᴛᴇᴍꜱ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ"))

            bot_details = await app.get_me()
            log.info(f"Bot Configured: Name: {bot_details.first_name}, ID: {bot_details.id}, Username: @{bot_details.username}")

        loop.run_until_complete(initialize_async_components())
        log.info(to_small_caps("ᴄᴏᴍᴍᴀɴᴅ ꜱʏꜱᴛᴇᴍ • ᴏɴʟɪɴᴇ"))
        idle()
        cleanup()
        app.stop()

    except Exception as e:
        log.exception(to_small_caps("ꜱʏꜱᴛᴇᴍ ꜰᴀɪʟᴜʀᴇ • ᴄʀɪᴛɪᴄᴀʟ ᴇʀʀᴏʀ"))
