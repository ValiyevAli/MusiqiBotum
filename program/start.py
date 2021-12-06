from datetime import datetime
from sys import version_info
from time import time

from config import (
    ALIVE_IMG,
    ALIVE_NAME,
    BOT_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_NAME,
    UPDATES_CHANNEL,
)
from program import __version__
from driver.veez import user
from driver.filters import command, other_filters
from pyrogram import Client, filters
from pyrogram import __version__ as pyrover
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("həftə", 60 * 60 * 24 * 7),
    ("gün", 60 * 60 * 24),
    ("saat", 60 * 60),
    ("dəqiqə", 60),
    ("saniyə", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@Client.on_message(
    command(["start", f"start@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f""" Salam {message.from_user.mention()}! **Snactus ⚡️ sizi salamlayır.**\n
Botu qrupa əlavə edərək həm musiqi dinləyə həmdə video və ya kino izləyə bilərsiz.


 **Botun komandaları haqqında bilgi almaq üçün Komandalar butonuna basın!**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Məni qrupa əlavə et",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🧔🏻 Sahibim",
                        url=f"https://t.me/ValiyevAli",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Dəstək qrupu", url=f"https://t.me/{GROUP_SUPPORT}"
                    ),
                    InlineKeyboardButton(
                        "📣 Rəsmi kanal", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],

            ]
        ),
        disable_web_page_preview=True,
    )



@Client.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    ass_uname = (await user.get_me()).username
    bot_id = (await c.get_me()).id
    for member in m.new_chat_members:
        if member.id == bot_id:
            return await m.reply(
                "**Məni qrupa əlavə etdiyiniz üçün təşəkkür edirəm. Aşağdan dəstək qrupumuza qatıla bilərsiniz.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✅ Rəsmi Kanal", url=f"https://t.me/{UPDATES_CHANNEL}"),
                            InlineKeyboardButton("❤️ Dəstək qrupu", url=f"https://t.me/{GROUP_SUPPORT}")
                        ],
                        [
                            InlineKeyboardButton("👤 Asistan", url=f"https://t.me/{ass_uname}")
                        ]
                    ]
                )
            )
