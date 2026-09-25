import os
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from database import DB_PATH
from helpers import cancel_keyboard, admin_main_keyboard
from handlers.admin.admin_core import is_admin

async def adm_backup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zahira nusxa (Backup & Restore) asosiy menyusi"""
    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Baza nusxasini yuklab olish", callback_data="adm_download_backup")],
        [InlineKeyboardButton("📤 Bazani qayta tiklash (Upload)", callback_data="adm_restore_backup")],
    ])
    await update.message.reply_text(
        "💾 <b>Zahira nusxalarni boshqarish</b>\n\n"
        "Bu yerdan botning joriy ma'lumotlar bazasini yuklab olishingiz yoki oldingi nusxasini yuklab qayta tiklashingiz mumkin.",
        parse_mode="HTML",
        reply_markup=kbd
    )

async def adm_download_backup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bazani yuborish"""
    query = update.callback_query
    await query.answer()

    if not os.path.exists(DB_PATH):
        await query.message.reply_text("❌ Baza fayli topilmadi!")
        return

    await query.message.reply_text("⏳ Fayl yuklanmoqda...")
    with open(DB_PATH, "rb") as f:
        await query.message.reply_document(document=f, filename="database.sqlite", caption="💾 Botning joriy ma'lumotlar bazasi.")

async def adm_restore_backup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restore jarayonini boshlash"""
    query = update.callback_query
    await query.answer()

    context.user_data["adm_action"] = "wait_db_upload"
    
    await query.message.delete()
    await query.message.chat.send_message(
        "⚠️ <b>DIQQAT! Bazani qayta tiklash xavfli jarayon!</b>\n\n"
        "Eski bazani yuklaganingizda, undan keyingi barcha ma'lumotlar (yangi foydalanuvchilar, to'lovlar, raqamlar) <b>O'CHIB KETADI</b>.\n\n"
        "Iltimos, qayta tiklash uchun <code>.sqlite</code> formatidagi faylni shu yerga yuboring:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def adm_receive_db_document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuborilgan hujjatni ushlab olish va bazaga yozish"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    if context.user_data.get("adm_action") != "wait_db_upload":
        return

    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Iltimos, fayl yuboring (document).")
        return

    if not doc.file_name.endswith(".sqlite"):
        await update.message.reply_text("❌ Noto'g'ri fayl formati! Faqat <code>.sqlite</code> fayl qabul qilinadi.", parse_mode="HTML")
        return

    await update.message.reply_text("⏳ Baza fayli qabul qilinmoqda, kuting...")

    try:
        file = await context.bot.get_file(doc.file_id)
        # Faylni to'g'ridan to'g'ri DB_PATH ga yozamiz
        await file.download_to_drive(DB_PATH)
        
        # Bazani qayta initsializatsiya qilamiz
        await db.init_db()

        context.user_data.pop("adm_action", None)
        await update.message.reply_text(
            "✅ <b>Baza muvaffaqiyatli qayta tiklandi!</b>",
            parse_mode="HTML",
            reply_markup=admin_main_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Faylni yuklashda yoki bazani ulashda xatolik yuz berdi:\n\n{e}")
