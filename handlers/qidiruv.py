import re
import unicodedata

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database as db
from config import EXCHANGE_RATE, SPIDER_API_KEY
from countries import COUNTRY_NAMES, get_country_name
from helpers import admin_main_keyboard, cancel_keyboard, main_menu_keyboard
from handlers.admin.admin_core import is_admin
from handlers.user.user_core import _get_lang
from spider_api import SpiderAPI
import strings as s

spider = SpiderAPI(SPIDER_API_KEY)


def _normalize_country_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    value = re.sub(r"[ʻʼ’‘`´]", "'", value)
    return " ".join(value.split())


def search_country(query: str) -> tuple[str, str] | None:
    """Davlat kodi va ko'rsatiladigan nomini qaytaradi."""
    normalized_query = re.sub(
        r"^[^\w]+", "", _normalize_country_name(query), flags=re.UNICODE
    )
    if not normalized_query:
        return None

    for code, name in COUNTRY_NAMES.items():
        plain_name = re.sub(r"^[^\w]+", "", name, flags=re.UNICODE)
        if normalized_query in {
            _normalize_country_name(code),
            _normalize_country_name(plain_name),
        }:
            return code, name
    return None


async def user_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    context.user_data["awaiting_search"] = True
    context.user_data["user_search_active"] = True
    await update.message.reply_text(
        s.SEARCH_PROMPT.get(lang, s.SEARCH_PROMPT["uz"]),
        reply_markup=cancel_keyboard(lang),
    )


async def user_search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    if update.message.text in s.MENU_CANCEL.values():
        context.user_data.pop("awaiting_search", None)
        context.user_data.pop("user_search_active", None)
        for key in ("pending_country", "pending_price", "pending_country_name"):
            context.user_data.pop(key, None)
        await update.message.reply_text(
            s.BUY_CANCELLED.get(lang, s.BUY_CANCELLED["uz"]),
            reply_markup=main_menu_keyboard(await is_admin(user_id), lang),
        )
        return

    if not context.user_data.get("awaiting_search"):
        return

    result = search_country(update.message.text or "")

    if result is None:
        text = (
            s.SEARCH_NOT_FOUND.get(lang, s.SEARCH_NOT_FOUND["uz"])
            + "\n"
            + s.SEARCH_PROMPT.get(lang, s.SEARCH_PROMPT["uz"])
        )
        await update.message.reply_text(
            text,
            reply_markup=cancel_keyboard(lang),
        )
        return

    code, country_name = result
    price = await db.get_setting(f"country_{code}")
    if price is None:
        await update.message.reply_text(
            s.SEARCH_NOT_ON_SALE.get(lang, s.SEARCH_NOT_ON_SALE["uz"]).format(
                country=country_name
            ),
            reply_markup=cancel_keyboard(lang),
        )
        return

    text = s.SEARCH_RESULT.get(lang, s.SEARCH_RESULT["uz"]).format(
        country=country_name,
        price=f"{int(float(price)):,}",
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            s.SEARCH_BUY_BTN.get(lang, s.SEARCH_BUY_BTN["uz"]),
            callback_data=f"select_country_{code}",
        ),
        InlineKeyboardButton(
            s.SEARCH_OTHER_COUNTRIES_BTN.get(
                lang, s.SEARCH_OTHER_COUNTRIES_BTN["uz"]
            ),
            callback_data="show_countries",
        ),
    ]])
    context.user_data.pop("awaiting_search", None)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def admin_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    lang = await _get_lang(user_id)
    context.user_data["adm_action"] = "search_country"
    context.user_data["admin_search_active"] = True
    await update.message.reply_text(
        s.SEARCH_PROMPT.get(lang, s.SEARCH_PROMPT["uz"]),
        reply_markup=cancel_keyboard(lang),
    )


async def admin_search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    lang = await _get_lang(user_id)
    if update.message.text in s.MENU_CANCEL.values():
        for key in ("adm_action", "target_country", "target_country_name"):
            context.user_data.pop(key, None)
        context.user_data.pop("admin_search_active", None)
        await update.message.reply_text(
            s.BUY_CANCELLED.get(lang, s.BUY_CANCELLED["uz"]),
            reply_markup=admin_main_keyboard(),
        )
        return

    result = search_country(update.message.text or "")
    if result is None:
        text = (
            s.SEARCH_NOT_FOUND.get(lang, s.SEARCH_NOT_FOUND["uz"])
            + "\n"
            + s.SEARCH_PROMPT.get(lang, s.SEARCH_PROMPT["uz"])
        )
        await update.message.reply_text(
            text,
            reply_markup=cancel_keyboard(lang),
        )
        return

    code, country_name = result
    price = await db.get_setting(f"country_{code}")
    if price is not None:
        original_price = await db.get_setting(f"country_{code}_original")
        if original_price is None:
            api_countries = await spider.get_countries()
            api_price = api_countries.get(code) if api_countries else None
            if api_price is not None:
                original_price = str(int(float(api_price) * EXCHANGE_RATE))

        text = s.ADMIN_SEARCH_RESULT.get(lang, s.ADMIN_SEARCH_RESULT["uz"]).format(
            country=country_name,
            code=code,
            original_price=(
                f"{int(float(original_price)):,}"
                if original_price is not None
                else "Noma'lum"
            ),
            sale_price=f"{int(float(price)):,}",
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                s.ADMIN_SEARCH_EDIT_BTN.get(lang, s.ADMIN_SEARCH_EDIT_BTN["uz"]),
                callback_data=f"admin_search_edit_{code}",
            ),
            InlineKeyboardButton(
                s.ADMIN_SEARCH_DELETE_BTN.get(lang, s.ADMIN_SEARCH_DELETE_BTN["uz"]),
                callback_data=f"admin_search_delete_{code}",
            ),
        ]])
    else:
        text = s.ADMIN_SEARCH_NOT_ON_SALE.get(
            lang, s.ADMIN_SEARCH_NOT_ON_SALE["uz"]
        ).format(country=country_name)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                s.ADMIN_SEARCH_ADD_BTN.get(lang, s.ADMIN_SEARCH_ADD_BTN["uz"]),
                callback_data=f"admin_search_add_{code}",
            ),
        ]])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def admin_search_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.answer()
        return

    code = query.data.removeprefix("admin_search_edit_")
    price = await db.get_setting(f"country_{code}")
    if price is None:
        await query.answer("Bu davlat endi sotuvda emas.", show_alert=True)
        return
    await query.answer()

    lang = await _get_lang(user_id)
    country_name = get_country_name(code)
    api_countries = await spider.get_countries()
    if not api_countries:
        await query.message.reply_text(
            "❌ API dan davlatlar narxini olib bo'lmadi. Keyinroq urinib ko'ring."
        )
        return

    context.user_data.update({
        "adm_action": "set_country_price",
        "target_country": code,
        "target_country_name": country_name,
        "country_selection_mode": "edit",
        "country_search_origin": True,
        "admin_search_active": True,
        "api_countries": api_countries,
    })
    api_price = api_countries.get(code)
    api_price_uzs = (
        f"{int(float(api_price) * EXCHANGE_RATE):,} so'm"
        if api_price
        else "Noma'lum"
    )
    await query.message.delete()
    await query.message.chat.send_message(
        f"🌍 {country_name} ({code})\n"
        f"Amaldagi sotuv narxi: {int(float(price)):,} so'm\n"
        f"Asl narxi (API dagi): {api_price_uzs}\n\n"
        "Yangi sotish narxini so'mda kiriting:",
        reply_markup=cancel_keyboard(lang),
    )


async def admin_search_delete_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.answer()
        return

    await query.answer()
    code = query.data.removeprefix("admin_search_delete_")
    country_name = get_country_name(code)
    await db.del_setting(f"country_{code}")
    first_page_order = await db.get_setting("purchase_first_page_order")
    selected = [
        item for item in (first_page_order or "").split(",")
        if item != code
    ]
    await db.set_setting("purchase_first_page_order", ",".join(selected))
    await query.message.edit_text(
        s.ADMIN_SEARCH_DELETED.get(
            await _get_lang(user_id), s.ADMIN_SEARCH_DELETED["uz"]
        ).format(country=country_name)
    )


async def admin_search_add_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.answer()
        return

    code = query.data.removeprefix("admin_search_add_")
    if await db.get_setting(f"country_{code}") is not None:
        await query.answer("Bu davlat allaqachon sotuvda.", show_alert=True)
        return
    await query.answer()

    api_countries = await spider.get_countries()
    if not api_countries or code not in api_countries:
        await query.message.reply_text(
            "❌ Bu davlat API da mavjud emas yoki API bilan bog'lanib bo'lmadi."
        )
        return

    lang = await _get_lang(user_id)
    country_name = get_country_name(code)
    api_price = api_countries[code]
    context.user_data.update({
        "adm_action": "set_country_price",
        "target_country": code,
        "target_country_name": country_name,
        "country_selection_mode": "add",
        "country_search_origin": True,
        "admin_search_active": True,
        "api_countries": api_countries,
    })
    await query.message.delete()
    await query.message.chat.send_message(
        f"🌍 {country_name} ({code})\n"
        f"Asl narxi (API dagi): {int(float(api_price) * EXCHANGE_RATE):,} so'm\n\n"
        "Sotish narxini so'mda kiriting:",
        reply_markup=cancel_keyboard(lang),
    )


async def search_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qidiruv tugmasini user yoki admin oqimiga yo'naltiradi."""
    user_id = update.effective_user.id
    if await is_admin(user_id) and context.user_data.get("admin_panel"):
        await admin_search_handler(update, context)
        return
    await user_search_handler(update, context)
