from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

import database as db
from helpers import cancel_keyboard
from handlers.user.user_core import ensure_subscribed
from handlers.admin.admin_core import is_admin


async def deposit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'💳 Hisobni to'ldirish' tugmasi"""
    if not await ensure_subscribed(update, context):
        return

    card_number = await db.get_setting("card_number")
    card_owner = await db.get_setting("card_owner")

    if not card_number:
        await update.message.reply_text("❌ Hozircha hisobni to'ldirish imkonsiz. Adminga murojaat qiling.")
        return

    context.user_data["awaiting_deposit_check"] = True
    
    import time
    import asyncio
    session_id = time.time()
    context.user_data["deposit_session_id"] = session_id

    async def deposit_timeout(chat_id, s_id):
        await asyncio.sleep(300)
        if context.user_data.get("awaiting_deposit_check") and context.user_data.get("deposit_session_id") == s_id:
            context.user_data.pop("awaiting_deposit_check", None)
            context.user_data.pop("deposit_session_id", None)
            from helpers import main_menu_keyboard
            try:
                is_admin_user = await is_admin(chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏳ To'lov qilish uchun berilgan 5 daqiqa vaqt tugadi. To'lov bekor qilindi.",
                    reply_markup=main_menu_keyboard(is_admin_user)
                )
            except Exception:
                pass

    asyncio.create_task(deposit_timeout(update.effective_chat.id, session_id))

    await update.message.reply_text(
        f"💳 <b>Hisobni to'ldirish</b>\n\n"
        f"Karta raqami: <code>{card_number}</code>\n"
        f"Qabul qiluvchi: <b>{card_owner}</b>\n\n"
        f"👇 Kerakli summani o'tkazgach, to'lov <b>cheki (skrinshotini)</b> shu yerga yuboring.\n"
        f"⚠️ <i>Sizda to'lovni tasdiqlash uchun 5 daqiqa vaqt bor.</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


async def deposit_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchidan to'lov chekini (rasm) qabul qilish"""
    user = update.effective_user

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Iltimos, to'lov chekini (rasm/skrinshot) yuboring yoki '❌ Bekor qilish' tugmasini bosing."
        )
        return

    photo_file_id = update.message.photo[-1].file_id

    # Adminlarga xabar yuborish
    from config import ADMIN_IDS
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    await update.message.reply_text(
        "✅ To'lov chekingiz adminga yuborildi. Tez orada hisobingiz to'ldiriladi.",
        reply_markup=cancel_keyboard()
    )

    context.user_data["awaiting_deposit_check"] = False
    from helpers import main_menu_keyboard
    await update.message.reply_text("🏠 Bosh menyu", reply_markup=main_menu_keyboard(await is_admin(user.id)))

    for admin_id in ADMIN_IDS:
        try:
            kbd = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Tasdiqlash va pul qo'shish", callback_data=f"confirm_dep_{user.id}")
            ]])
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo_file_id,
                caption=(
                    f"📥 <b>Yangi to'lov cheki!</b>\n\n"
                    f"👤 Foydalanuvchi: {user.full_name}\n"
                    f"🆔 ID: <code>{user.id}</code>\n"
                    f"Username: @{user.username if user.username else 'yoq'}\n\n"
                    f"👇 Tasdiqlash uchun pastdagi tugmani bosing va summani yozing."
                ),
                parse_mode="HTML",
                reply_markup=kbd
            )
        except Exception:
            pass
