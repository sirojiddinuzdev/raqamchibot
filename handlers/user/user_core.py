import logging
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import database as db
from countries import get_country_name
from helpers import (
    check_user_subscribed,
    build_subscribe_keyboard,
    main_menu_keyboard,
    lang_select_keyboard,
)
from handlers.admin.admin_core import is_admin
import strings as s

logger = logging.getLogger(__name__)


async def chat_join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi majburiy kanalga qo'shilish so'rovi yuborganda"""
    user_id = update.chat_join_request.from_user.id
    chat_id = update.chat_join_request.chat.id
    await db.add_join_request(user_id, chat_id)


async def _get_lang(user_id: int) -> str:
    """Foydalanuvchi tilini qaytaradi"""
    return await db.get_user_lang(user_id)


async def ensure_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """False qaytarsa — obuna bo'lmagan"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    channels = await db.get_channels()
    if channels:
        not_subs = await check_user_subscribed(context.bot, user_id, channels)
        if not_subs:
            kbd = build_subscribe_keyboard(not_subs, "check_sub", lang)
            text = s.SUB_REQUIRED.get(lang, s.SUB_REQUIRED["uz"]) + "\n".join(f"• {ch['channel_name']}" for ch in not_subs)
            msg = update.message or (update.callback_query.message if update.callback_query else None)
            if msg:
                await msg.reply_text(text, parse_mode="HTML", reply_markup=kbd)
            return False

    await _confirm_referral(update, context)
    return True


async def _confirm_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    referrer_id = await db.confirm_referral(user.id)
    if referrer_id is None:
        return

    referral_count = await db.get_referral_count(referrer_id)
    referrer_lang = await _get_lang(referrer_id)
    referred_name = html.escape(user.full_name or str(user.id))
    referral_messages = {
        "uz": (
            f"🎉 Sizning referral havolangiz orqali "
            f"<b>{referred_name}</b> qo'shildi!\n"
            f"🏆 Jami ballaringiz: <b>{referral_count}</b>"
        ),
        "en": (
            f"🎉 <b>{referred_name}</b> joined through your referral link!\n"
            f"🏆 Your total points: <b>{referral_count}</b>"
        ),
        "ru": (
            f"🎉 По вашей реферальной ссылке присоединился "
            f"<b>{referred_name}</b>!\n"
            f"🏆 Всего баллов: <b>{referral_count}</b>"
        ),
    }
    try:
        await context.bot.send_message(
            chat_id=referrer_id,
            text=referral_messages.get(referrer_lang, referral_messages["uz"]),
            parse_mode="HTML",
        )
    except TelegramError:
        logger.exception(
            "Could not notify referrer %s about new referral %s",
            referrer_id,
            user.id,
        )


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    context.user_data.pop("admin_panel", None)

    ref_id = None
    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id == user_id:
                ref_id = None
        except ValueError:
            pass

    existing = await db.get_user(user_id)
    if not existing:
        if ref_id is not None and not await db.get_user(ref_id):
            ref_id = None
        await db.create_user(
            user_id=user_id,
            username=user.username or "",
            full_name=user.full_name or "",
            referred_by=ref_id
        )
        existing = await db.get_user(user_id)

    lang = await _get_lang(user_id)
    if not await ensure_subscribed(update, context):
        return
    if existing["is_banned"]:
        await update.message.reply_text(s.BANNED.get(lang, s.BANNED["uz"]))
        return

    safe_name = html.escape(user.first_name)
    text = s.WELCOME.get(lang, s.WELCOME["uz"]).format(
        name=safe_name,
        balance=f"{int(existing['balance']):,}",
        user_id=user_id,
    )
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(user_id), lang),
    )


async def set_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Til tanlash callback"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.replace("set_lang_", "")

    if lang not in ("uz", "en", "ru"):
        lang = "uz"

    await db.set_user_lang(user_id, lang)

    # Tilni tasdiqlash
    await query.message.edit_text(
        s.LANG_CHANGED.get(lang, s.LANG_CHANGED["uz"]),
        reply_markup=None
    )

    # Obuna tekshirish va asosiy menyuga o'tish
    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        await query.message.chat.send_message(s.BANNED.get(lang, s.BANNED["uz"]))
        return

    balance = user_data["balance"] if user_data else 0.0
    safe_name = html.escape(query.from_user.first_name)
    is_admin_user = await is_admin(user_id)

    text = s.WELCOME.get(lang, s.WELCOME["uz"]).format(
        name=safe_name,
        balance=f"{int(balance):,}",
        user_id=user_id
    )
    await query.message.chat.send_message(
        text, parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin_user, lang)
    )


async def change_lang_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'🌐 Til / Language / Язык' tugmasi"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    await update.message.reply_text(
        s.CHOOSE_LANGUAGE.get(lang, s.CHOOSE_LANGUAGE["uz"]),
        parse_mode="HTML",
        reply_markup=lang_select_keyboard()
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _get_lang(user_id)

    channels = await db.get_channels()
    not_subs = await check_user_subscribed(context.bot, user_id, channels)

    if not_subs:
        await query.answer(s.SUB_NOT_YET.get(lang, s.SUB_NOT_YET["uz"]), show_alert=True)
        kbd = build_subscribe_keyboard(not_subs, "check_sub", lang)
        new_text = s.SUB_FAIL.get(lang, s.SUB_FAIL["uz"]) + "\n".join(f"• {ch['channel_name']}" for ch in not_subs)
        if query.message.text != new_text:
            try:
                await query.message.edit_text(new_text, parse_mode="HTML", reply_markup=kbd)
            except Exception:
                pass
    else:
        await _confirm_referral(update, context)
        user_data = await db.get_user(user_id)
        balance = user_data["balance"] if user_data else 0.0
        await query.message.delete()
        safe_name = html.escape(query.from_user.first_name)
        text = s.SUB_CONFIRMED.get(lang, s.SUB_CONFIRMED["uz"]).format(
            name=safe_name,
            balance=f"{int(balance):,}",
            user_id=user_id
        )
        await query.message.chat.send_message(
            text, parse_mode="HTML",
            reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
        )


async def back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'🔙 Bosh menyuga / Back to menu / В главное меню' tugmasi"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    context.user_data.clear()

    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        await update.message.reply_text(s.BANNED.get(lang, s.BANNED["uz"]))
        return

    balance = user_data["balance"] if user_data else 0.0
    text = s.MAIN_MENU_TEXT.get(lang, s.MAIN_MENU_TEXT["uz"]).format(
        balance=f"{int(balance):,}",
        user_id=user_id
    )
    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
    )


async def my_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'💰 Hisobim / My balance / Мой баланс' tugmasi"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)

    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if not user_data:
        await update.message.reply_text(s.USER_NOT_FOUND.get(lang, s.USER_NOT_FOUND["uz"]))
        return

    safe_fullname = html.escape(user_data['full_name'])
    referral_count = await db.get_referral_count(user_id)
    text = s.BALANCE_TEXT.get(lang, s.BALANCE_TEXT["uz"]).format(
        name=safe_fullname,
        user_id=user_id,
        balance=f"{int(user_data['balance']):,}",
        referrals=referral_count,
        joined=user_data['joined_at'][:10]
    )

    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    s.ACCOUNT_DEPOSIT_BTN.get(lang, s.ACCOUNT_DEPOSIT_BTN["uz"]),
                    callback_data="start_deposit",
                )
            ],
            [
                InlineKeyboardButton(
                    s.ACCOUNT_PROMO_BTN.get(lang, s.ACCOUNT_PROMO_BTN["uz"]),
                    callback_data="start_promo",
                ),
            ]
        ]),
    )


async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchining muvaffaqiyatli xarid qilingan raqamlari tarixi"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    query = update.callback_query
    if query:
        await query.answer()
        page = int(query.data.rsplit("_", 1)[1])
    else:
        page = 0

    if not await ensure_subscribed(update, context):
        return

    completed_purchases = await db.get_user_purchase_history(user_id, offset=page * 10)
    has_next_page = len(completed_purchases) > 10
    completed_purchases = completed_purchases[:10]
    message = update.message or query.message

    if not completed_purchases:
        await message.reply_text(
            s.HISTORY_EMPTY.get(lang, s.HISTORY_EMPTY["uz"]),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    s.ACCOUNT_DEPOSIT_BTN.get(lang, s.ACCOUNT_DEPOSIT_BTN["uz"]),
                    callback_data="start_deposit",
                )
            ]]),
        )
        return

    history_text = s.HISTORY_HEADER.get(lang, s.HISTORY_HEADER["uz"])
    for index, purchase in enumerate(completed_purchases, start=page * 10 + 1):
        bought_at = html.escape(purchase["bought_at"] or "")
        number = html.escape(purchase["number"] or "")
        country = html.escape(get_country_name(purchase["country"] or ""))
        history_text += (
            f"{index}. {country}\n"
            f"📅 {bought_at}\n"
            f"🔢 <code>{number}</code>\n"
            f"💵 {int(purchase['price']):,} so'm\n\n"
        )

    page_buttons = []
    if page > 0:
        page_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"history_page_{page - 1}"))
    if has_next_page:
        page_buttons.append(InlineKeyboardButton("➡️", callback_data=f"history_page_{page + 1}"))
    keyboard = InlineKeyboardMarkup([page_buttons]) if page_buttons else None

    if query:
        await message.edit_text(history_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.reply_text(
            history_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


async def contact_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'📞 Admin bilan bog'lanish / Contact admin' tugmasi"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    if not await ensure_subscribed(update, context):
        return

    from config import SUPPORT_LINK
    text = s.CONTACT_ADMIN_TEXT.get(lang, s.CONTACT_ADMIN_TEXT["uz"]).format(link=SUPPORT_LINK)
    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
    )


async def referral_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    if not await ensure_subscribed(update, context):
        return

    bot_info = await context.bot.get_me()
    if not bot_info.username:
        raise RuntimeError("Telegram bot username is unavailable for referral links.")

    referral_link = f"https://t.me/{bot_info.username}?start={user_id}"
    messages = {
        "uz": f"🔗 Sizning referral havolangiz:\n{referral_link}\n\n"
              "Havola orqali yangi foydalanuvchi taklif qilsangiz, har biri uchun 1 ball olasiz.",
        "en": f"🔗 Your referral link:\n{referral_link}\n\n"
              "Earn 1 point for each new user who joins through your link.",
        "ru": f"🔗 Ваша реферальная ссылка:\n{referral_link}\n\n"
              "Получайте 1 балл за каждого нового пользователя, пришедшего по вашей ссылке.",
    }
    await update.message.reply_text(messages.get(lang, messages["uz"]))


async def referral_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    if not await ensure_subscribed(update, context):
        return

    own_referrals, leaderboard = await db.get_referral_stats(user_id)
    headers = {
        "uz": f"🏆 Sizning ballaringiz: <b>{own_referrals}</b>\n"
              "🏅 <b>Eng ko'p taklif qilganlar (Top 10):</b>\n\n",
        "en": f"🏆 Your points: <b>{own_referrals}</b>\n"
              "🏅 <b>Top 10 referrers:</b>\n\n",
        "ru": f"🏆 Ваши баллы: <b>{own_referrals}</b>\n"
              "🏅 <b>Топ 10 пригласивших:</b>\n\n",
    }
    empty = {
        "uz": "Hozircha takliflar yo'q.",
        "en": "No referrals yet.",
        "ru": "Пока нет приглашённых пользователей.",
    }
    lines = []
    for rank, referrer in enumerate(leaderboard, start=1):
        display_name = html.escape(
            referrer["full_name"] or str(referrer["user_id"])
        )
        lines.append(f"{rank}. {display_name} — <b>{referrer['referrals']}</b>")

    await update.message.reply_text(
        headers.get(lang, headers["uz"]) + ("\n".join(lines) or empty.get(lang, empty["uz"])),
        parse_mode="HTML",
    )
