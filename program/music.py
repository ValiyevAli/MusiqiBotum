# Co
# C
# 

import re
import asyncio

from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch


def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1)
        for r in search.result()["result"]:
            ytid = r["id"]
            if len(r["title"]) > 34:
                songname = r["title"][:70]
            else:
                songname = r["title"]
            url = f"https://www.youtube.com/watch?v={ytid}"
        return [songname, url]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
async def play(c: Client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="❄️ Menyu", callback_data="cbmenu"),
                InlineKeyboardButton(text="🎄 Bağla", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous Admin__ !\n\n» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Mənim **Administrator** **permissions** və aşağıdakı haqqlarım olmalıdır:\n\n» ❌ __Mesaj silmə__\n» ❌ __İstifadəçi əlavə etmə__\n» ❌ __Görüntülü söhbəti idarə etmə__\n\n"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "Xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __Görüntülü söhbəti idarə etmə__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __Mesaj silmə__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __İstifadəçi əlavə etmə__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} adlı asistan {m.chat.title} adlı qrupdan atılıb.\n\n» **botun banını açın.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **userbot xəta**\n\n**səbəb**: `{e}`")
                return
        else:
            try:
                user_id = (await user.get_me()).id
                link = await c.export_chat_invite_link(chat_id)
                if "+" in link:
                    link_hash = (link.replace("+", "")).split("t.me/")[1]
                    await ubot.join_chat(link_hash)
                await c.promote_member(chat_id, user_id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **userbot qrupa qatıla bilmədi**\n\n**reason**: `{e}`"
                )
    if replied:
        if replied.audio or replied.voice:
            suhu = await replied.reply("📥 **audio yüklənnir...**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:70]
                else:
                    if replied.audio.file_name:
                        songname = replied.audio.file_name[:70]
                    else:
                        songname = "Audio"
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Musiqi sıraya əlavə olundu »** `{pos}`\n\n🏷 **Ad:** [{songname}]({link})\n💭 **Qrup ID:** `{chat_id}`\n🎧 {m.from_user.mention()} tərəfindən.",
                    reply_markup=keyboard,
                )
            else:
             try:
                await suhu.edit("☃️ **Asistan səsli söhbətə qoşulur...**")
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"💡 **Musiqi başladı.**\n\n🏷 **Ad:** [{songname}]({link})\n💭 **Qrup ID:** `{chat_id}`\n💡 **Status:** `Hal hazırda səsli söhbətdə dinlənilir`\n🎧  {requester} tərəfindən.",
                    reply_markup=keyboard,
                )
             except Exception as e:
                await suhu.delete()
                await m.reply_text(f"🚫 error:\n\n» {e}")
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» xəta"
                )
            else:
                suhu = await c.send_message(chat_id, "❄️ **Axtarılır...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **heçnə tapa bilmədim (**")
                else:
                    songname = search[0]
                    url = search[1]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Audio", 0
                            )
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_1}",
                                caption=f"💡 **Musiqi sıraya alındı »** `{pos}`\n\n🏷 **Ad:** [{songname}]({url})\n💭 **Qrup ID:** `{chat_id}`\n🎧 {requester} tərəfindən.",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await suhu.edit("🎄 **Asistan səsli söhbətə qoşulur...**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_2}",
                                    caption=f"💡 **Musiqi səsli söhbətdə başladı.**\n\n🏷 **Ad:** [{songname}]({url})\n💭 **Qrup ID:** `{chat_id}`\n💡 **Status:** `dinlənilir`\n🎧 {requester} tərəfindən.",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫 error: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» reply to an **audio file** or **give something to search.**"
            )
        else:
            suhu = await c.send_message(chat_id, "❄️ **Axtarılır...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("❌ **axtarış nəticə vermədi.**")
            else:
                songname = search[0]
                url = search[1]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await suhu.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=f"{IMG_1}",
                            caption=f"💡 Musiqi sıraya alındı `{pos}`\n\n🏷 **Ad:** [{songname}]({url})\n💭 **Qrup ID:** `{chat_id}`\n🎧 {requester} tərəfindən...",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await suhu.edit("🎄 **Asistan səsli söhbətə qoşulur...**")
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_2}",
                                caption=f"💡 **Musiqi səsli söhbətdə ifa olunur..**\n\n🏷 **Ad:** [{songname}]({url})\n💭 **Qrup ID:** `{chat_id}`\n💡 **Status:** `dinlənilir`\n🎧 {requester} tərəfindən...",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await suhu.delete()
                            await m.reply_text(f"🚫 error: `{ep}`")


# stream is used for live streaming only


@Client.on_message(command(["stream", f"stream@{BOT_USERNAME}"]) & other_filters)
async def stream(c: Client, m: Message):
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="❄️ Menyu", callback_data="cbmenu"),
                InlineKeyboardButton(text="🎄 Bağla", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous Admin__ !\n\n» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"Xəta zəhmət olmasa mənim bütün yetkilərimi verin."
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __Görüntülü söhbəti idarə etmə__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __Delete messages__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("xəta aşağıda yazılan yetkim yoxdur:" + "\n\n» ❌ __Add users__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"**@{ASSISTANT_NAME} adlı asistanın banın açın!**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **asistan səsli söhbətə qoşula bilmədi**\n\n**səbəb**: `{e}`")
                return
        else:
            try:
                user_id = (await user.get_me()).id
                link = await c.export_chat_invite_link(chat_id)
                if "+" in link:
                    link_hash = (link.replace("+", "")).split("t.me/")[1]
                    await ubot.join_chat(link_hash)
                await c.promote_member(chat_id, user_id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **asistan səsli söhbətə qoşula bilmədi**\n\n**reason**: `{e}`"
                )

    if len(m.command) < 2:
        await m.reply("» give me a live-link/m3u8 url/youtube link to stream.")
    else:
        link = m.text.split(None, 1)[1]
        suhu = await c.send_message(chat_id, "🎄 **processing stream...**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            veez, livelink = await ytdl(link)
        else:
            livelink = link
            veez = 1

        if veez == 0:
            await suhu.edit(f"❌ yt-dl issues detected\n\n» `{livelink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Radio", livelink, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Musiqi sıraya əlavə olundu »** `{pos}`\n\n💭 **Qrup ID:** `{chat_id}`\n🎧 {requester} tərəfindən...",
                    reply_markup=keyboard,
                )
            else:
                try:
                    await suhu.edit("🎄 **Asistan səsli söhbətə qoşulur...**")
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(
                            livelink,
                        ),
                        stream_type=StreamType().live_stream,
                    )
                    add_to_queue(chat_id, "Radio", livelink, link, "Audio", 0)
                    await suhu.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{IMG_2}",
                        caption=f"💡 **Musiqi başladı.**\n\n💭 **Qrup ID:** `{chat_id}`\n💡 **Status:** `dinlənilir`\n🎧 {requester} tərəfindən...",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await suhu.delete()
                    await m.reply_text(f"🚫 error: `{ep}`")
