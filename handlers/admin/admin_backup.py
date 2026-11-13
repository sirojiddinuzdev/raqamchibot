import io
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from helpers import cancel_keyboard, admin_main_keyboard
from handlers.admin.admin_core import is_admin

logger = logging.getLogger(__name__)

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
    """PostgreSQL bazasining JSON nusxasini yuborish."""
    query = update.callback_query
    await query.answer()

    if not await is_admin(query.from_user.id):
        return

    try:
        backup = await db.export_backup()
        await query.message.reply_document(
            document=io.BytesIO(backup),
            filename="database_backup.json",
            caption="💾 Botning PostgreSQL bazasi nusxasi.",
        )
    except Exception:
        logger.exception("Failed to export admin PostgreSQL backup")
        await query.message.reply_text("❌ Baza nusxasini yaratishda xatolik yuz berdi.")

async def adm_restore_backup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restore jarayonini boshlash"""
    query = update.callback_query
    await query.answer()
    if not await is_admin(query.from_user.id):
        return

    context.user_data["adm_action"] = "wait_db_upload"
    
    await query.message.delete()
    await query.message.chat.send_message(
        "⚠️ <b>DIQQAT! Bazani qayta tiklash xavfli jarayon!</b>\n\n"
        "Eski bazani yuklaganingizda, undan keyingi barcha ma'lumotlar (yangi foydalanuvchilar, to'lovlar, raqamlar) <b>O'CHIB KETADI</b>.\n\n"
        "Iltimos, <code>.json</code> formatidagi PostgreSQL nusxasini yoki "
        "<code>.sqlite</code> formatidagi SQLite nusxasini yuboring:",
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

    file_name = (doc.file_name or "").lower()
    if not file_name.endswith((".json", ".sqlite")):
        await update.message.reply_text(
            "❌ Noto'g'ri fayl formati! <code>.json</code> yoki "
            "<code>.sqlite</code> zaxira fayli yuboring.",
            parse_mode="HTML",
        )
        return

    await update.message.reply_text("⏳ Baza qayta tiklanmoqda, kuting...")

    try:
        file = await context.bot.get_file(doc.file_id)
        buffer = io.BytesIO()
        await file.download_to_memory(buffer)
        if file_name.endswith(".sqlite"):
            await db.restore_sqlite_backup(buffer.getvalue())
        else:
            payload = json.loads(buffer.getvalue())
            await db.restore_backup(payload)

        context.user_data.pop("adm_action", None)
        await update.message.reply_text(
            "✅ <b>Baza muvaffaqiyatli qayta tiklandi!</b>",
            parse_mode="HTML",
            reply_markup=admin_main_keyboard()
        )
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        logger.warning("Rejected invalid database backup: %s", error)
        await update.message.reply_text(
            "❌ Fayl yaroqsiz yoki qo‘llab-quvvatlanmaydigan zaxira nusxasi."
        )
    except Exception:
        logger.exception("Failed to restore database backup")
        await update.message.reply_text(
            "❌ Baza nusxasini tiklashda xatolik yuz berdi. "
            "Baza o‘zgartirilmagan bo‘lishi kerak; loglarni tekshiring."
        )
