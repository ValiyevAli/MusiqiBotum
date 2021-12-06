from cache.admins import admins
from driver.veez import call_py
from pyrogram import Client, filters
from driver.decorators import authorized_users_only
from driver.filters import command, other_filters
from driver.queues import QUEUE, clear_queue
from driver.utils import skip_current_song, skip_item
from config import BOT_USERNAME, GROUP_SUPPORT, IMG_3, UPDATES_CHANNEL
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


bttn = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Geri", callback_data="cbmenu")]]
)


bcl = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Bağla", callback_data="cls")]]
)


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        "✅ Bot **Yeniləndi !**\n✅ **Admin siyahısı** yeniləndi."
    )


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "vskip"]) & other_filters)
@authorized_users_only
async def skip(client, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="❄️ Menyu", callback_data="cbmenu"
                ),
                InlineKeyboardButton(
                    text="🎄 Bağla", callback_data="cls"
                ),
            ]
        ]
    )

    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("❌ nothing is currently playing")
        elif op == 1:
            await m.reply("✅ __Sırada__ ** musiqi olmadığı üçün asistan səsli söhbətdən çıxdı.**")
        elif op == 2:
            await m.reply("🗑️ **Sıradakılar təmizlənir**\n\n**• asistan səsli söhbətdən çıxdı.**")
        else:
            await m.reply_photo(
                photo=f"{IMG_3}",
                caption=f"⏭ **Skip olundu.**\n\n🏷 **Adı:** [{op[0]}]({op[1]})\n💭 **Qrup ID:** `{chat_id}`\n💡 **Status:** `dinlənilir`\n🎧 {m.from_user.mention()} tərəfindən.",
                reply_markup=keyboard,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "🗑 **Sıradakılar silindi:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(
    command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}", "vstop"])
    & other_filters
)
@authorized_users_only
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("✅ **Musiqi dayandırıldı.**")
        except Exception as e:
            await m.reply(f"🚫 **Xəta: :**\n\n`{e}`")
    else:
        await m.reply("❌ **hal hazırda dinlədiyiniz və ya izlədiyiniz bir şey yoxdur**")


@Client.on_message(
    command(["pause", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                "⏸ **Musiqiyə pauza verildi.**\n\n• /resume yazaraq qaldığınız yerdən davam edə bilərsiniz."
            )
        except Exception as e:
            await m.reply(f"🚫 Xəta:  \n\n`{e}`")
    else:
        await m.reply("❌ **heç birşey izlənilmir**")


@Client.on_message(
    command(["resume", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                "▶️ **Musiqi davam edir.**"
            )
        except Exception as e:
            await m.reply(f"🚫 Xəta: \n\n`{e}`")
    else:
        await m.reply("❌ **heç birşey izlənilmir**")