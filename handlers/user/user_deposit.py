from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from telegram.ext import ContextTypes

import database as db
from helpers import cancel_keyboard, main_menu_keyboard
from handlers.user.user_core import ensure_subscribed, _get_lang
from handlers.admin.admin_core import is_admin
import strings as s


async def deposit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisobni to'ldirish tugmasi"""
    await _request_deposit_amount(update, context)


async def start_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _request_deposit_amount(update, context)


async def _request_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_subscribed(update, context):
        return

    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    message = update.message or update.callback_query.message

    card_number = await db.get_setting("card_number")
    if not card_number:
        await message.reply_text(s.DEPOSIT_NO_CARD.get(lang, s.DEPOSIT_NO_CARD["uz"]))
        return

    context.user_data["awaiting_deposit_amount"] = True
    await message.reply_text(
        s.DEPOSIT_ENTER_AMOUNT.get(lang, s.DEPOSIT_ENTER_AMOUNT["uz"]),
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang)
    )


async def start_deposit_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Summa kiritilgandan keyin kartani ko'rsatish va rasmni kutish"""
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)

    card_number = await db.get_setting("card_number")
    card_owner = await db.get_setting("card_owner")
    amount = context.user_data.get("deposit_amount", 0)

    context.user_data["awaiting_deposit_check"] = True

    import time
    import asyncio
    session_id = time.time()
    context.user_data["deposit_session_id"] = session_id

    is_admin_user = await is_admin(update.effective_chat.id)

    async def deposit_timeout(chat_id, s_id, is_admin_flag, lang_):
        await asyncio.sleep(300)
        if context.user_data.get("awaiting_deposit_check") and context.user_data.get("deposit_session_id") == s_id:
            context.user_data.pop("awaiting_deposit_check", None)
            context.user_data.pop("deposit_session_id", None)
            context.user_data.pop("deposit_amount", None)
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=s.DEPOSIT_TIMEOUT.get(lang_, s.DEPOSIT_TIMEOUT["uz"]),
                    reply_markup=main_menu_keyboard(is_admin_flag, lang_)
                )
            except Exception:
                pass

    asyncio.create_task(deposit_timeout(update.effective_chat.id, session_id, is_admin_user, lang))

    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 {card_number}", copy_text=CopyTextButton(text=card_number.replace(" ", "")))],
        [InlineKeyboardButton(f"💰 {amount:,}", copy_text=CopyTextButton(text=str(amount)))],
        [InlineKeyboardButton("❌ Bekor qilish / Cancel / Отмена", callback_data="cancel_deposit")]
    ])

    text = s.DEPOSIT_DETAILS.get(lang, s.DEPOSIT_DETAILS["uz"]).format(
        amount=f"{amount:,}",
        card=card_number,
        owner=card_owner or ""
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kbd)


async def cancel_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = await _get_lang(user_id)

    context.user_data.pop("awaiting_deposit_check", None)
    context.user_data.pop("deposit_session_id", None)
    context.user_data.pop("deposit_amount", None)

    await query.message.edit_text(s.DEPOSIT_CANCELLED.get(lang, s.DEPOSIT_CANCELLED["uz"]))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=s.MAIN_MENU_TEXT.get(lang, s.MAIN_MENU_TEXT["uz"]).format(balance="—", user_id=user_id),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
    )


async def deposit_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchidan to'lov chekini (rasm) qabul qilish"""
    import html as html_mod
    import time as time_mod

    user = update.effective_user
    lang = await _get_lang(user.id)

    if not update.message.photo and not update.message.document:
        await update.message.reply_text(s.DEPOSIT_INVALID.get(lang, s.DEPOSIT_INVALID["uz"]))
        return

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        is_doc = False
    else:
        file_id = update.message.document.file_id
        is_doc = True

    amount = context.user_data.get("deposit_amount", 0)

    from handlers.admin.admin_core import get_all_admin_ids
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    all_admins = await get_all_admin_ids()
    dep_id = f"dep_{user.id}_{int(time_mod.time())}"

    await update.message.reply_text(
        s.DEPOSIT_SENT.get(lang, s.DEPOSIT_SENT["uz"]),
        reply_markup=cancel_keyboard(lang)
    )

    context.user_data.pop("awaiting_deposit_check", None)
    context.user_data.pop("deposit_session_id", None)
    context.user_data.pop("deposit_amount", None)

    await update.message.reply_text(
        "🏠",
        reply_markup=main_menu_keyboard(await is_admin(user.id), lang)
    )

    admin_msgs = []
    for admin_id in all_admins:
        try:
            kbd = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Tasdiqlash va pul qo'shish", callback_data=f"confirm_dep_{dep_id}")],
                [InlineKeyboardButton("❌ Qabul qilmaslik", callback_data=f"reject_dep_{dep_id}")]
            ])
            caption_text = (
                f"📥 <b>Yangi to'lov cheki!</b>\n\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={user.id}'>{html_mod.escape(user.full_name)}</a>\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"Username: @{user.username if user.username else 'yoq'}\n"
                f"So'ralgan summa: <b>{amount:,} so'm</b>\n\n"
                f"👇 Tasdiqlash yoki rad etish uchun pastdagi tugmani bosing."
            )
            if is_doc:
                msg = await context.bot.send_document(
                    chat_id=admin_id, document=file_id,
                    caption=caption_text, parse_mode="HTML", reply_markup=kbd
                )
            else:
                msg = await context.bot.send_photo(
                    chat_id=admin_id, photo=file_id,
                    caption=caption_text, parse_mode="HTML", reply_markup=kbd
                )
            admin_msgs.append((admin_id, msg.message_id))
        except Exception:
            pass

    if "deposits" not in context.bot_data:
        context.bot_data["deposits"] = {}

    context.bot_data["deposits"][dep_id] = {
        "user_id": user.id,
        "amount": amount,
        "admin_msgs": admin_msgs
    }
