import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from database import DB_PATH
from helpers import cancel_keyboard, paginated_keyboard
from config import SPIDER_API_KEY, EXCHANGE_RATE
from spider_api import SpiderAPI
from countries import get_country_name
from handlers.admin.admin_core import is_admin

spider = SpiderAPI(SPIDER_API_KEY)


async def adm_countries_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🌍 Davlatlar tugmasi (Admin panel)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute("SELECT key, value FROM settings WHERE key LIKE 'country_%'") as cur:
            rows = await cur.fetchall()

    api_countries = await spider.get_countries()

    text = "🌍 <b>Sotuvdagi davlatlar ro'yxati (Botda):</b>\n\n"
    if not rows:
        text += "Hozircha davlatlar qo'shilmagan."
    else:
        for k, v in rows:
            c_code = k.replace("country_", "")
            c_name = get_country_name(c_code)
            api_price_usd = api_countries.get(c_code)
            if api_price_usd:
                api_price_uzs = f"{int(float(api_price_usd) * EXCHANGE_RATE):,.0f} so'm"
            else:
                api_price_uzs = "Noma'lum"
            sale_price = f"{int(float(v)):,.0f} so'm" if v else "0 so'm"
            text += f"• {c_name} ({c_code}): Asl: <b>{api_price_uzs}</b> | Sotuv: <b>{sale_price}</b>\n"

    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Davlat qo'shish", callback_data="adm_add_country_list")],
        [InlineKeyboardButton("✏️ Tahrirlash", callback_data="adm_edit_country_list")],
        [InlineKeyboardButton("➖ Davlatni o'chirish", callback_data="adm_remove_country_list")]
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kbd)


async def adm_add_country_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text("⏳ API dan davlatlar olinmoqda...")
    api_countries = await spider.get_countries()

    if not api_countries:
        await query.message.edit_text("❌ API bilan ulanishda xatolik yoki davlatlar yo'q.")
        return

    context.user_data["api_countries"] = api_countries
    context.user_data["adm_clist_page"] = 0

    items = []
    for code, price in api_countries.items():
        name = get_country_name(code)
        price_uzs = int(float(price) * EXCHANGE_RATE)
        items.append((f"adm_pick_country_{code}", f"{name} ({price_uzs:,} so'm)"))

    kbd = paginated_keyboard(items, 0, per_page=15, prefix="adm_clist")
    await query.message.edit_text(
        "🌍 <b>Qo'shish uchun davlatni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=kbd
    )


async def adm_clist_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])
    context.user_data["adm_clist_page"] = page

    api_countries = context.user_data.get("api_countries", {})
    items = []
    for code, price in api_countries.items():
        name = get_country_name(code)
        price_uzs = int(float(price) * EXCHANGE_RATE)
        items.append((f"adm_pick_country_{code}", f"{name} ({price_uzs:,} so'm)"))

    kbd = paginated_keyboard(items, page, per_page=15, prefix="adm_clist")
    await query.message.edit_reply_markup(reply_markup=kbd)


async def adm_pick_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("adm_pick_country_", "")
    name = get_country_name(code)

    context.user_data["adm_action"] = "set_country_price"
    context.user_data["target_country"] = code
    context.user_data["target_country_name"] = name
    
    api_price = context.user_data.get("api_countries", {}).get(code)
    if api_price:
        api_price_uzs = f"{int(float(api_price) * EXCHANGE_RATE):,} so'm"
    else:
        api_price_uzs = "Noma'lum"

    await query.message.delete()
    await query.message.chat.send_message(
        f"🌍 Siz <b>{name}</b> ({code}) ni tanladingiz.\n"
        f"Asl narxi (API dagi): <b>{api_price_uzs}</b>\n\n"
        f"Sotish narxini so'mda kiriting (masalan: 15000):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def adm_edit_country_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute("SELECT key FROM settings WHERE key LIKE 'country_%'") as cur:
            rows = await cur.fetchall()

    if not rows:
        await query.message.edit_text("❌ Hozircha davlatlar qo'shilmagan.")
        return

    # To show original prices if needed, load api_countries
    api_countries = await spider.get_countries()
    context.user_data["api_countries"] = api_countries

    items = []
    for k in rows:
        code = k[0].replace("country_", "")
        name = get_country_name(code)
        items.append((f"adm_pick_country_{code}", name))

    kbd_buttons = []
    for cb_data, btn_text in items:
        kbd_buttons.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

    await query.message.edit_text(
        "✏️ <b>Narxini tahrirlash uchun davlatni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kbd_buttons)
    )


async def adm_remove_country_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute("SELECT key FROM settings WHERE key LIKE 'country_%'") as cur:
            rows = await cur.fetchall()

    if not rows:
        await query.message.edit_text("❌ Hozircha davlatlar qo'shilmagan.")
        return

    items = []
    for k in rows:
        code = k[0].replace("country_", "")
        name = get_country_name(code)
        items.append((f"adm_del_country_{code}", name))

    # O'chirish uchun hamma davlatlar bitta sahifada qila qolamiz (odatda 10-20 ta bo'ladi)
    kbd_buttons = []
    for cb_data, btn_text in items:
        kbd_buttons.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

    await query.message.edit_text(
        "❌ <b>O'chirish uchun davlatni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kbd_buttons)
    )


async def adm_del_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("adm_del_country_", "")
    name = get_country_name(code)

    await db.del_setting(f"country_{code}")
    await query.message.edit_text(f"✅ <b>{name}</b> sotuvdan olib tashlandi.", parse_mode="HTML")


async def adm_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📢 Kanallar tugmasi (Admin)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    channels = await db.get_channels()
    text = "📢 <b>Majburiy obuna kanallari:</b>\n\n"
    for ch in channels:
        text += f"• {ch['channel_name']} (<code>{ch['channel_id']}</code>)\n"

    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Kanal qo'shish", callback_data="adm_add_channel")],
        [InlineKeyboardButton("➖ Kanalni o'chirish", callback_data="adm_remove_channel")]
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kbd)


async def adm_add_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adm_action"] = "add_channel"
    await query.message.delete()
    await query.message.chat.send_message(
        "➕ Yangi kanal ID sini yoki username sini kiriting (masalan: @kanal_nomi yoki -100...):",
        reply_markup=cancel_keyboard()
    )


async def adm_remove_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channels = await db.get_channels()
    if not channels:
        await query.message.edit_text("❌ Kanallar yo'q.")
        return

    kbd = []
    for ch in channels:
        kbd.append([InlineKeyboardButton(ch["channel_name"], callback_data=f"adm_del_ch_{ch['id']}")])

    await query.message.edit_text("❌ Qaysi kanalni olib tashlamoqchisiz?", reply_markup=InlineKeyboardMarkup(kbd))


async def adm_del_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chid = int(query.data.split("_")[-1])
    await db.del_channel(chid)
    await query.message.edit_text("✅ Kanal olib tashlandi.")


async def adm_set_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💳 Karta sozlash (Admin)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    card_num = await db.get_setting("card_number")
    card_owner = await db.get_setting("card_owner")

    context.user_data["adm_action"] = "set_card_number"
    await update.message.reply_text(
        f"Joriy karta: {card_num}\nEgasi: {card_owner}\n\n"
        f"Yangi karta raqamini kiriting (masalan: 8600 0000 0000 0000):",
        reply_markup=cancel_keyboard()
    )
