from Yumeko import app 
from pyrogram.errors import RPCError
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message , ChatPrivileges , ChatPermissions
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import ChatPermissions
from threading import RLock
from time import perf_counter
from cachetools import TTLCache

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()

async def resolve_user(client: app, message: Message):  # type: ignore
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if message.command:
            args = message.command[1:]
            if args:
                query = args[0]

                if query.isdigit():
                    try:
                        return await app.get_users(int(query))
                    except RPCError:
                        return None

                if query.startswith("@"):
                    try:
                        return await app.get_users(query)
                    except RPCError:
                        return None

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.TEXT_MENTION and entity.user:
                    return entity.user

        return None

    except PeerIdInvalid:
        return None


DEMOTE = ChatPrivileges(
                            can_delete_messages = False,
                            can_manage_video_chats = False,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_edit_messages = False,
                            can_invite_users = False,
                            can_pin_messages = False,
                            is_anonymous = False
            )

PROMOTE = ChatPrivileges(
                            can_delete_messages = True,
                            can_manage_video_chats = True,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_invite_users = True,
                            can_pin_messages = True,
                            is_anonymous = False
            )

FULLPROMOTE = ChatPrivileges(
                            can_delete_messages = True,
                            can_manage_video_chats = True,
                            can_restrict_members = True,
                            can_promote_members = True,
                            can_change_info = True,
                            can_invite_users = True,
                            can_pin_messages = True,
                            is_anonymous = False
            )

LOWPROMOTE = ChatPrivileges(
                            can_delete_messages = False,
                            can_manage_video_chats = False,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_invite_users = True,
                            can_pin_messages = True,
                            is_anonymous = False
            )

async def resolve_user_for_afk(client: app, message: Message):  # type: ignore
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if message.command:
            args = message.command[1:]
            if args:
                query = args[0]

                if query.isdigit():
                    try:
                        return await app.get_users(int(query))
                    except RPCError:
                        return None

                if query.startswith("@"):
                    try:
                        return await app.get_users(query)
                    except RPCError:
                        return None

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.TEXT_MENTION and entity.user:
                    return entity.user
                elif entity.type == MessageEntityType.MENTION and entity.user:
                    return entity.user

        return None

    except PeerIdInvalid:
        return None

MUTE = ChatPermissions()
UNMUTE = ChatPermissions(
    can_send_messages = True,
    can_send_media_messages = True,
    can_send_other_messages = True,
    can_send_polls = True,
    can_add_web_page_previews = True,
    can_change_info = True,
    can_invite_users = True,
    can_pin_messages = True
)
RESTRICT = ChatPermissions(
    can_send_messages = True,
    can_send_media_messages = False,
    can_send_other_messages = False,
    can_send_polls = False,
    can_add_web_page_previews = False,
    can_change_info = False,
    can_invite_users = False,
    can_pin_messages = False
)



# Define permissions for night mode
NIGHT_MODE_PERMISSIONS = ChatPermissions(
    can_send_messages = True,
    can_send_media_messages = False,
    can_send_other_messages = False,
    can_send_polls = False,
    can_add_web_page_previews = False,
    can_change_info = False,
    can_invite_users = False,
    can_pin_messages = False
)

DEFAULT_PERMISSIONS = ChatPermissions(
    can_send_messages = True,
    can_send_media_messages = True,
    can_send_other_messages = True,
    can_send_polls = True,
    can_add_web_page_previews = True,
    can_change_info = True,
    can_invite_users = True,
    can_pin_messages = True
)
