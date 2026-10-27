from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiosqlite
import html

import database as db
from database import DB_PATH
from helpers import main_menu_keyboard, paginated_keyboard
from countries import get_country_name
from spider_api import SpiderAPI
from config import SPIDER_API_KEY
from handlers.user.user_core import ensure_subscribed, _get_lang
from handlers.admin.admin_core import is_admin
import strings as s

spider = SpiderAPI(SPIDER_API_KEY)


async def _load_country_items() -> list[tuple[str, str, float]]:
    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT key, value FROM settings WHERE key LIKE 'country_%' AND key NOT LIKE '%_original'"
        ) as cur:
            rows = await cur.fetchall()

    countries = []
    for key, value in rows:
        code = key.replace("country_", "")
        try:
            countries.append((code, get_country_name(code), float(value)))
        except (TypeError, ValueError):
            continue
    return countries


async def _get_country_menu_items() -> list[tuple[str, str]]:
    countries = await _load_country_items()
    alphabetical = sorted(countries, key=lambda item: item[1].casefold())

    first_page_order = await db.get_setting("purchase_first_page_order")
    selected_codes = [code for code in (first_page_order or "").split(",") if code]
    active_by_code = {code: (code, name, price) for code, name, price in alphabetical}

    featured = [active_by_code[code] for code in selected_codes if code in active_by_code]
    featured_codes = {code for code, _, _ in featured}
    remaining = [item for item in alphabetical if item[0] not in featured_codes]

    countries = featured + remaining
    return [
        (f"select_country_{code}", f"{name} | {int(price):,} so'm")
        for code, name, price in countries
    ]


def _country_keyboard(items: list[tuple[str, str]], page: int, lang: str) -> InlineKeyboardMarkup:
    start = 0 if page == 0 else 14 + (page - 1) * 10
    page_size = 14 if page == 0 else 10
    end = min(start + page_size, len(items))
    buttons = [
        [InlineKeyboardButton(label, callback_data=callback_data)]
        for callback_data, label in items[start:end]
    ]

    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton("⬅️", callback_data=f"page_country_{page - 1}"))
    if end < len(items):
        navigation.append(InlineKeyboardButton("➡️", callback_data=f"page_country_{page + 1}"))
    if navigation:
        buttons.append(navigation)

    if page == 0:
        buttons.insert(0, [InlineKeyboardButton(
            s.BUY_TOP_CHEAP_BTN.get(lang, s.BUY_TOP_CHEAP_BTN["uz"]),
            callback_data="top_cheap_countries",
        )])
    return InlineKeyboardMarkup(buttons)


async def buy_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_subscribed(update, context):
        return

    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        await update.message.reply_text(s.BANNED.get(lang, s.BANNED["uz"]))
        return

    await update.message.reply_text(s.LOADING_COUNTRIES.get(lang, s.LOADING_COUNTRIES["uz"]))

    items = await _get_country_menu_items()
    if not items:
        await update.message.reply_text(
            s.NO_COUNTRIES.get(lang, s.NO_COUNTRIES["uz"]),
            reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
        )
        return

    kbd = _country_keyboard(items, 0, lang)
    context.user_data["country_page"] = 0
    await update.message.reply_text(
        s.SELECT_COUNTRY.get(lang, s.SELECT_COUNTRY["uz"]),
        parse_mode="HTML",
        reply_markup=kbd
    )


async def country_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = 0 if query.data == "show_countries" else int(query.data.split("_")[-1])
    context.user_data["country_page"] = page
    lang = await _get_lang(query.from_user.id)
    items = await _get_country_menu_items()
    keyboard = _country_keyboard(items, page, lang)
    if query.data == "show_countries":
        await query.message.edit_text(
            s.SELECT_COUNTRY.get(lang, s.SELECT_COUNTRY["uz"]),
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await query.message.edit_reply_markup(reply_markup=keyboard)


async def top_10_countries_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        return

    page = 0
    if query and query.data.startswith("page_topcheap_"):
        page = int(query.data.rsplit("_", 1)[1])

    countries = sorted(await _load_country_items(), key=lambda item: item[2])
    items = [
        (f"select_country_{code}", f"{name} | {int(price):,} so'm")
        for code, name, price in countries
    ]
    keyboard = paginated_keyboard(items, page, per_page=10, prefix="topcheap", lang=lang)
    buttons = list(keyboard.inline_keyboard)
    buttons.append([InlineKeyboardButton(
        s.TOP10_ALL_BTN.get(lang, s.TOP10_ALL_BTN["uz"]),
        callback_data="show_countries"
    )])

    text = s.TOP10_TITLE.get(lang, s.TOP10_TITLE["uz"])
    keyboard = InlineKeyboardMarkup(buttons)
    if query:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def select_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    country_code = query.data.replace("select_country_", "")

    user_id = query.from_user.id
    lang = await _get_lang(user_id)
    user_data = await db.get_user(user_id)

    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT value FROM settings WHERE key=?",
            (f"country_{country_code}",)
        ) as cur:
            row = await cur.fetchone()

    if not row:
        await query.answer(s.COUNTRY_UNAVAILABLE.get(lang, s.COUNTRY_UNAVAILABLE["uz"]), show_alert=True)
        return

    price = float(row[0])
    country_name = get_country_name(country_code)
    balance = user_data["balance"] if user_data else 0.0

    context.user_data["pending_country"] = country_code
    context.user_data["pending_price"] = price
    context.user_data["pending_country_name"] = country_name

    if balance >= price:
        text = s.CONFIRM_BUY.get(lang, s.CONFIRM_BUY["uz"]).format(
            country=country_name,
            price=f"{int(price):,}",
            balance=f"{int(balance):,}"
        )
        kbd = InlineKeyboardMarkup([[
            InlineKeyboardButton(s.BUY_CONFIRM_BTN.get(lang, s.BUY_CONFIRM_BTN["uz"]), callback_data="confirm_buy"),
            InlineKeyboardButton(s.BUY_CANCEL_BTN.get(lang, s.BUY_CANCEL_BTN["uz"]), callback_data="cancel_buy"),
        ]])
    else:
        text = s.INSUFFICIENT_BALANCE.get(lang, s.INSUFFICIENT_BALANCE["uz"]).format(
            country=country_name,
            price=f"{int(price):,}",
            balance=f"{int(balance):,}",
            diff=f"{int(price - balance):,}"
        )
        kbd = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    s.BUY_CANCEL_BTN.get(lang, s.BUY_CANCEL_BTN["uz"]),
                    callback_data="cancel_buy",
                )
            ],
            [
                InlineKeyboardButton(
                    s.ACCOUNT_DEPOSIT_BTN.get(lang, s.ACCOUNT_DEPOSIT_BTN["uz"]),
                    callback_data="start_deposit",
                )
            ],
        ])

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=kbd)


async def cancel_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _get_lang(user_id)
    context.user_data.pop("pending_country", None)
    context.user_data.pop("pending_price", None)
    context.user_data.pop("pending_country_name", None)
    await query.message.delete()
    await query.message.chat.send_message(
        s.BUY_CANCELLED.get(lang, s.BUY_CANCELLED["uz"]),
        reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
    )


async def confirm_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang = await _get_lang(user_id)
    user_data = await db.get_user(user_id)

    country_code = context.user_data.pop("pending_country", None)
    price = context.user_data.pop("pending_price", None)
    country_name = context.user_data.pop("pending_country_name", None)

    if not country_code or not price:
        await query.message.edit_text(s.PURCHASE_ERROR.get(lang, s.PURCHASE_ERROR["uz"]))
        return

    if not await db.decrease_balance(user_id, price):
        await query.answer(s.BALANCE_INSUFFICIENT_ALERT.get(lang, s.BALANCE_INSUFFICIENT_ALERT["uz"]), show_alert=True)
        return

    await query.message.edit_text(s.BUYING_LOADING.get(lang, s.BUYING_LOADING["uz"]))

    result = await spider.get_number(country_code)

    if not result:
        await db.update_balance(user_id, price)
        await query.message.edit_text(
            s.NO_NUMBER_FOUND.get(lang, s.NO_NUMBER_FOUND["uz"]),
            parse_mode="HTML"
        )
        return

    number = result["number"]
    hash_code = result["hash_code"]

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
        user_id=user_id, country=country_code, country_name=country_name,
        number=number, hash_code=hash_code, price=price, original_price=original_price
    )

    from config import LOG_CHANNEL
    if LOG_CHANNEL:
        try:
            log_text = (
                f"🛒 <b>Yangi xarid!</b>\n\n"
                f"👤 Xaridor: <a href='tg://user?id={user_id}'>{html.escape(query.from_user.first_name)}</a> (<code>{user_id}</code>)\n"
                f"🌍 Davlat: {country_name}\n"
                f"📱 Raqam: <code>{number[:-4]}****</code>\n"
                f"💵 Narxi: {int(price):,} so'm\n\n"
                f"🤖Bot havolasi:\n"
                f"@tgraqamchi_bot"
            )
            await context.bot.send_message(
                chat_id=LOG_CHANNEL,
                text=log_text,
                parse_mode="HTML",
            )
        except Exception:
            pass

    u_record = await db.get_user(user_id)
    new_balance = u_record["balance"] if u_record else 0

    kbd = InlineKeyboardMarkup([[
        InlineKeyboardButton(s.GET_CODE_BTN.get(lang, s.GET_CODE_BTN["uz"]), callback_data=f"get_code_{purchase_id}")
    ]])

    text = s.BUY_SUCCESS.get(lang, s.BUY_SUCCESS["uz"]).format(
        country=country_name,
        number=number,
        price=f"{int(price):,}",
        balance=f"{int(new_balance):,}"
    )
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=kbd)


async def get_code_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await _get_lang(user_id)
    await query.answer("⏳")

    purchase_id = int(query.data.replace("get_code_", ""))
    purchase = await db.get_purchase(purchase_id)

    if not purchase:
        await query.answer(s.PURCHASE_NOT_FOUND.get(lang, s.PURCHASE_NOT_FOUND["uz"]), show_alert=True)
        return

    if purchase["status"] == "completed" and purchase["code"]:
        password_val = purchase['password'] or ('Mavjud emas' if lang == 'uz' else ('Not available' if lang == 'en' else 'Нет'))
        text = s.CODE_ALREADY.get(lang, s.CODE_ALREADY["uz"]).format(
            country=purchase['country_name'],
            number=purchase['number'],
            code=purchase['code'],
            password=password_val
        )
        await query.message.edit_text(text, parse_mode="HTML")
        return

    result = await spider.get_code(purchase["hash_code"])

    if not result or not result.get("code"):
        kbd = InlineKeyboardMarkup([[
            InlineKeyboardButton(s.RETRY_BTN.get(lang, s.RETRY_BTN["uz"]), callback_data=f"get_code_{purchase_id}")
        ]])
        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")
        try:
            await query.message.edit_text(
                s.CODE_WAITING.get(lang, s.CODE_WAITING["uz"]).format(
                    country=purchase['country_name'],
                    number=purchase['number'],
                    time=now_str
                ),
                parse_mode="HTML",
                reply_markup=kbd
            )
        except Exception:
            pass
        return

    code = result["code"]
    password = result.get("password", "")

    await db.set_purchase_code(purchase_id, code, password)

    password_val = password or ('Mavjud emas' if lang == 'uz' else ('Not available' if lang == 'en' else 'Нет'))
    text = s.CODE_ARRIVED.get(lang, s.CODE_ARRIVED["uz"]).format(
        country=purchase['country_name'],
        number=purchase['number'],
        price=f"{int(purchase['price']):,}",
        code=code,
        password=password_val
    )
    await query.message.edit_text(text, parse_mode="HTML")
