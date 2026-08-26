from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_IDS
from helpers import admin_main_keyboard, cancel_keyboard


async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panelga kirish /admin"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔️ Siz admin emassiz.")
        return

    context.user_data.clear()
    await update.message.reply_text(
        "👨‍💻 <b>Admin Panelga xush kelibsiz!</b>\n\nQuyidagi menyulardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=admin_main_keyboard()
    )


async def adm_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Statistika"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    users = await db.get_all_users()
    total_users = len(users)

    # Qisqa hisobot uchun eng so'nggi xaridlarni va umumiysini sanash kerak
    # DB dan barcha xaridlarni count va sum qilish mumkin:
    import aiosqlite
    from database import DB_PATH
    async with aiosqlite.connect(DB_PATH) as dbase:
        async with dbase.execute(
            "SELECT COUNT(*), SUM(price) FROM purchases WHERE status='completed'"
        ) as cur:
            row = await cur.fetchone()
            completed_purchases = row[0] or 0
            total_income = row[1] or 0.0

    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total_users}</b>\n"
        f"✅ Sotilgan raqamlar: <b>{completed_purchases}</b> ta\n"
        f"💵 Umumiy aylanma: <b>{total_income:.2f} $</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def adm_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📢 Xabar yuborish"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    context.user_data["adm_action"] = "broadcast"
    await update.message.reply_text(
        "📝 Hamma foydalanuvchilarga yuboriladigan xabarni kiriting (Rasm yoki matn):",
        reply_markup=cancel_keyboard()
    )
