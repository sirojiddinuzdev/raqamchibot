from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiosqlite

import database as db
from database import DB_PATH
from helpers import (
    main_menu_keyboard,
    paginated_keyboard,
)
from countries import get_country_name
from spider_api import SpiderAPI
from config import SPIDER_API_KEY
from handlers.user.user_core import ensure_subscribed
from handlers.admin.admin_core import is_admin

spider = SpiderAPI(SPIDER_API_KEY)


async def buy_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'📱 Raqam sotib olish' tugmasi"""
    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(update.effective_user.id)
    if user_data and user_data["is_banned"]:
        await update.message.reply_text("🚫 Siz bloklangansiz.")
        return

    await update.message.reply_text("⏳ Mavjud davlatlar yuklanmoqda...")

    # DB dan faqat admin qo'shgan davlatlarni olish
    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT key, value FROM settings WHERE key LIKE 'country_%' AND key NOT LIKE '%_original'"
        ) as cur:
            rows = await cur.fetchall()

    admin_countries = {}
    for key, val in rows:
        code = key.replace("country_", "")
        try:
            admin_countries[code] = float(val)
        except Exception:
            pass

    if not admin_countries:
        await update.message.reply_text(
            "❌ Hozircha sotuvda davlatlar yo'q.\nKeyinroq urinib ko'ring.",
            reply_markup=main_menu_keyboard(await is_admin(update.effective_user.id))
        )
        return

    items = []
    for code, price in admin_countries.items():
        name = get_country_name(code)
        items.append((f"select_country_{code}", f"{name} | {int(price):,} so'm"))

    items.sort(key=lambda x: x[1])  # sort by name

    kbd = paginated_keyboard(items, 0, per_page=14, prefix="country", back_callback=None)

    context.user_data["country_page"] = 0
    await update.message.reply_text(
        "🌍 <b>Davlat tanlang</b>\n\nQuyidagi davlatlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=kbd
    )


async def country_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])
    context.user_data["country_page"] = page

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT key, value FROM settings WHERE key LIKE 'country_%' AND key NOT LIKE '%_original'"
        ) as cur:
            rows = await cur.fetchall()

    admin_countries = {}
    for key, val in rows:
        code = key.replace("country_", "")
        try:
            admin_countries[code] = float(val)
        except Exception:
            pass

    items = []
    for code, price in admin_countries.items():
        name = get_country_name(code)
        items.append((f"select_country_{code}", f"{name} | {int(price):,} so'm"))

    items.sort(key=lambda x: x[1])

    kbd = paginated_keyboard(items, page, per_page=14, prefix="country", back_callback=None)
    
    await query.message.edit_reply_markup(reply_markup=kbd)





async def select_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    country_code = query.data.replace("select_country_", "")

    user_id = query.from_user.id
    user_data = await db.get_user(user_id)

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT value FROM settings WHERE key=?",
            (f"country_{country_code}",)
        ) as cur:
            row = await cur.fetchone()

    if not row:
        await query.answer("❌ Bu davlat hozir mavjud emas.", show_alert=True)
        return

    price = float(row[0])
    country_name = get_country_name(country_code)
    balance = user_data["balance"] if user_data else 0.0

    context.user_data["pending_country"] = country_code
    context.user_data["pending_price"] = price
    context.user_data["pending_country_name"] = country_name

    text = (
        f"🌍 <b>Tanlangan davlat:</b> {country_name}\n"
        f"💵 <b>Narxi:</b> {int(price):,} so'm\n"
        f"💰 <b>Balansingiz:</b> {int(balance):,} so'm\n\n"
    )

    if balance >= price:
        text += "✅ Balansingiz yetarli. Xaridni tasdiqlaysizmi?"
        kbd = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Ha, sotib olaman", callback_data="confirm_buy"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_buy"),
        ]])
    else:
        text += (
            f"❌ <b>Balansingiz yetarli emas!</b>\n"
            f"Kerakli: {int(price):,} so'm | Yetishmaydi: {int(price - balance):,} so'm\n\n"
            f"💳 Hisobni to'ldiring!"
        )
        kbd = InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_buy"),
        ]])

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=kbd)


async def cancel_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("pending_country", None)
    context.user_data.pop("pending_price", None)
    context.user_data.pop("pending_country_name", None)
    await query.message.delete()
    await query.message.chat.send_message(
        "❌ Bekor qilindi.",
        reply_markup=main_menu_keyboard(await is_admin(query.from_user.id))
    )


async def confirm_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data = await db.get_user(user_id)

    country_code = context.user_data.pop("pending_country", None)
    price = context.user_data.pop("pending_price", None)
    country_name = context.user_data.pop("pending_country_name", None)

    if not country_code or not price:
        await query.message.edit_text("❌ Xatolik. Qaytadan urinib ko'ring.")
        return

    # Atomic balance deduction
    if not await db.decrease_balance(user_id, price):
        await query.answer("❌ Balansingiz yetarli emas!", show_alert=True)
        return

    await query.message.edit_text("⏳ Raqam sotib olinmoqda, iltimos kuting...")

    result = await spider.get_number(country_code)

    if not result:
        # Refund on failure
        await db.update_balance(user_id, price)
        await query.message.edit_text(
            f"❌ <b>Bu davlat uchun raqam topilmadi!</b>\n"
            f"Boshqa davlatni tanlang yoki keyinroq urinib ko'ring.\n"
            f"(Pulingiz hisobingizga qaytarildi)",
            parse_mode="HTML"
        )
        return

    number = result["number"]
    hash_code = result["hash_code"]

    # Asl narxni olamiz
    original_price = 0.0
    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT value FROM settings WHERE key=?",
            (f"country_{country_code}_original",)
        ) as cur:
            row_orig = await cur.fetchone()
            if row_orig:
                original_price = float(row_orig[0])

    purchase_id = await db.create_purchase(
        user_id=user_id,
        country=country_code,
        country_name=country_name,
        number=number,
        hash_code=hash_code,
        price=price,
        original_price=original_price
    )

    from config import LOG_CHANNEL
    if LOG_CHANNEL:
        try:
            log_text = (
                f"🛒 <b>Yangi xarid!</b>\n\n"
                f"👤 Xaridor: <a href='tg://user?id={user_id}'>{query.from_user.first_name}</a> (<code>{user_id}</code>)\n"
                f"🌍 Davlat: {country_name}\n"
                f"📱 Raqam: <code>{number[:-4]}****</code>\n"
                f"💵 Narxi: {int(price):,} so'm"
            )
            await context.bot.send_message(chat_id=LOG_CHANNEL, text=log_text, parse_mode="HTML")
        except Exception:
            pass


    u_record = await db.get_user(user_id)
    new_balance = u_record["balance"] if u_record else 0

    kbd = InlineKeyboardMarkup([[
        InlineKeyboardButton("📨 SMS Kodni olish", callback_data=f"get_code_{purchase_id}")
    ]])

    await query.message.edit_text(
        f"✅ <b>Raqam muvaffaqiyatli sotib olindi!</b>\n\n"
        f"🌍 Davlat: {country_name}\n"
        f"📱 Raqam: <code>{number}</code>\n"
        f"💵 Narxi: {int(price):,} so'm\n"
        f"💰 Qolgan balans: {int(new_balance):,} so'm\n\n"
        f"📨 SMS kodni olish uchun tugmani bosing.",
        parse_mode="HTML",
        reply_markup=kbd
    )


async def get_code_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Kod tekshirilmoqda...")

    purchase_id = int(query.data.replace("get_code_", ""))
    purchase = await db.get_purchase(purchase_id)

    if not purchase:
        await query.answer("❌ Xarid topilmadi.", show_alert=True)
        return

    if purchase["status"] == "completed" and purchase["code"]:
        await query.message.edit_text(
            f"✅ <b>SMS Kod:</b>\n\n"
            f"🌍 Davlat: {purchase['country_name']}\n"
            f"📱 Raqam: <code>{purchase['number']}</code>\n"
            f"💬 <b>Kod: <code>{purchase['code']}</code></b>\n"
            f"🔑 Parol: <code>{purchase['password'] or 'Mavjud emas'}</code>",
            parse_mode="HTML"
        )
        return

    result = await spider.get_code(purchase["hash_code"])

    if not result or not result.get("code"):
        kbd = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Qayta tekshirish", callback_data=f"get_code_{purchase_id}")
        ]])
        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")
        try:
            await query.message.edit_text(
                f"⏳ <b>SMS kod hali kelmadi.</b> ({now_str})\n\n"
                "Biroz kuting va qayta tekshiring (1–3 daqiqa).",
                parse_mode="HTML",
                reply_markup=kbd
            )
        except Exception:
            pass
        return

    code = result["code"]
    password = result.get("password", "")

    await db.set_purchase_code(purchase_id, code, password)

    await query.message.edit_text(
        f"✅ <b>SMS Kod keldi!</b>\n\n"
        f"🌍 Davlat: {purchase['country_name']}\n"
        f"📱 Raqam: <code>{purchase['number']}</code>\n"
        f"💵 Narxi: {int(purchase['price']):,} so'm\n"
        f"💬 <b>Kod: <code>{code}</code></b>\n"
        f"🔑 Parol: <code>{password or 'Mavjud emas'}</code>\n\n"
        f"✅ Telegram ilovasida ushbu raqamni faollashtiring!",
        parse_mode="HTML"
    )
