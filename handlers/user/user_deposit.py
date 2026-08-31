from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import html

import database as db
from helpers import cancel_keyboard
from handlers.user.user_core import ensure_subscribed
from handlers.admin.admin_core import is_admin


async def deposit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'💳 Hisobni to'ldirish' tugmasi"""
    if not await ensure_subscribed(update, context):
        return

    card_number = await db.get_setting("card_number")
    if not card_number:
        await update.message.reply_text("❌ Hozircha hisobni to'ldirish imkonsiz. Adminga murojaat qiling.")
        return

    context.user_data["awaiting_deposit_amount"] = True
    await update.message.reply_text(
        "💰 <b>Qancha summa o'tkazmoqchisiz?</b>\n\nIltimos, summani raqamlarda kiriting (masalan: 50000):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


async def start_deposit_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Summa kiritilgandan keyin kartani ko'rsatish va rasmni kutish"""
    card_number = await db.get_setting("card_number")
    card_owner = await db.get_setting("card_owner")
    amount = context.user_data.get("deposit_amount", 0)

    context.user_data["awaiting_deposit_check"] = True
    
    import time
    import asyncio
    session_id = time.time()
    context.user_data["deposit_session_id"] = session_id

    is_admin_user = await is_admin(update.effective_chat.id)

    async def deposit_timeout(chat_id, s_id, is_admin_flag):
        await asyncio.sleep(300)
        if context.user_data.get("awaiting_deposit_check") and context.user_data.get("deposit_session_id") == s_id:
            context.user_data.pop("awaiting_deposit_check", None)
            context.user_data.pop("deposit_session_id", None)
            context.user_data.pop("deposit_amount", None)
            from helpers import main_menu_keyboard
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏳ To'lov qilish uchun berilgan 5 daqiqa vaqt tugadi. Vaqtingiz yetmagan bo'lsa, qaytadan 'Hisobni to'ldirish' tugmasi orqali urinib ko'rishingiz mumkin.",
                    reply_markup=main_menu_keyboard(is_admin_flag)
                )
            except Exception:
                pass

    asyncio.create_task(deposit_timeout(update.effective_chat.id, session_id, is_admin_user))

    from telegram import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 {card_number}", copy_text=CopyTextButton(text=card_number.replace(" ", "")))],
        [InlineKeyboardButton(f"💰 {amount:,} so'm", copy_text=CopyTextButton(text=str(amount)))],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_deposit")]
    ])

    await update.message.reply_text(
        f"💳 <b>Hisobni to'ldirish</b>\n\n"
        f"Kiritilgan summa: <b>{amount:,} so'm</b>\n\n"
        f"Karta raqami: <code>{card_number}</code>\n"
        f"Qabul qiluvchi: <b>{card_owner}</b>\n\n"
        f"👇 Ushbu kartaga <b>{amount:,} so'm</b> o'tkazgach, to'lov <b>cheki (skrinshotini)</b> shu yerga yuboring.\n"
        f"⚠️ <i>Sizda to'lovni tasdiqlash uchun 5 daqiqa vaqt bor.</i>",
        parse_mode="HTML",
        reply_markup=kbd
    )

async def cancel_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.pop("awaiting_deposit_check", None)
    context.user_data.pop("deposit_session_id", None)
    context.user_data.pop("deposit_amount", None)
    
    await query.message.edit_text("❌ Hisobni to'ldirish bekor qilindi.")
    from handlers.user.user_core import back_to_main_handler
    from helpers import main_menu_keyboard
    from handlers.admin.admin_core import is_admin
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🏠 Bosh menyu",
        reply_markup=main_menu_keyboard(await is_admin(update.effective_user.id))
    )


async def deposit_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchidan to'lov chekini (rasm) qabul qilish"""
    user = update.effective_user

    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "❌ Iltimos, to'lov chekini (rasm/skrinshot yoki fayl) yuboring yoki '❌ Bekor qilish' tugmasini bosing."
        )
        return

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        is_doc = False
    else:
        file_id = update.message.document.file_id
        is_doc = True
        
    amount = context.user_data.get("deposit_amount", 0)

    # Adminlarga xabar yuborish
    from handlers.admin.admin_core import get_all_admin_ids
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    import time

    all_admins = await get_all_admin_ids()
    dep_id = f"dep_{user.id}_{int(time.time())}"

    await update.message.reply_text(
        "✅ To'lov chekingiz adminga yuborildi. Tez orada hisobingiz to'ldiriladi.",
        reply_markup=cancel_keyboard()
    )

    context.user_data.pop("awaiting_deposit_check", None)
    context.user_data.pop("deposit_session_id", None)
    context.user_data.pop("deposit_amount", None)
    
    from helpers import main_menu_keyboard
    await update.message.reply_text("🏠 Bosh menyu", reply_markup=main_menu_keyboard(await is_admin(user.id)))

    admin_msgs = []
    for admin_id in all_admins:
        try:
            kbd = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Tasdiqlash va pul qo'shish", callback_data=f"confirm_dep_{dep_id}")],
                [InlineKeyboardButton("❌ Qabul qilmaslik", callback_data=f"reject_dep_{dep_id}")]
            ])
            caption_text = (
                f"📥 <b>Yangi to'lov cheki!</b>\n\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={user.id}'>{html.escape(user.full_name)}</a>\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"Username: @{user.username if user.username else 'yoq'}\n"
                f"So'ralgan summa: <b>{amount:,} so'm</b>\n\n"
                f"👇 Tasdiqlash yoki rad etish uchun pastdagi tugmani bosing."
            )
            if is_doc:
                msg = await context.bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=caption_text,
                    parse_mode="HTML",
                    reply_markup=kbd
                )
            else:
                msg = await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=caption_text,
                    parse_mode="HTML",
                    reply_markup=kbd
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

