from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_IDS
from helpers import admin_main_keyboard, cancel_keyboard


async def is_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    
    val = await db.get_setting("dynamic_admins")
    if val:
        admins = [int(x) for x in val.split(",") if x.strip()]
        if user_id in admins:
            return True
            
    return False


async def get_all_admin_ids() -> list:
    admins = list(ADMIN_IDS)
    val = await db.get_setting("dynamic_admins")
    if val:
        dyn = [int(x) for x in val.split(",") if x.strip()]
        admins.extend(dyn)
    return list(set(admins))


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
    completed_purchases = 0
    total_income = 0.0
    total_original = 0.0
    top_country = "Yo'q"

    import aiosqlite
    from database import DB_PATH
    async with aiosqlite.connect(DB_PATH) as dbase:
        dbase.row_factory = aiosqlite.Row
        async with dbase.execute(
            "SELECT country, SUM(price) as tot, COUNT(*) as c FROM purchases WHERE status='completed' GROUP BY country"
        ) as cur:
            rows = await cur.fetchall()

    if rows:
        top_row = max(rows, key=lambda x: x["c"])
        from countries import get_country_name
        top_country = get_country_name(top_row["country"])

        for r in rows:
            c = r["country"]
            count = r["c"]
            tot = r["tot"]

            completed_purchases += count
            total_income += tot

            orig = await db.get_setting(f"country_{c}_original")
            if orig:
                total_original += (float(orig) * count)

    profit = total_income - total_original

    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total_users}</b>\n"
        f"✅ Sotilgan raqamlar: <b>{completed_purchases}</b> ta\n"
        f"👑 Eng ko'p sotilgan davlat: <b>{top_country}</b>\n"
        f"💵 Asl narxi (Tan narxi): <b>{int(total_original):,} so'm</b>\n"
        f"💰 Biz sotgan narx: <b>{int(total_income):,} so'm</b>\n"
        f"📈 Sof foyda: <b>{int(profit):,} so'm</b>"
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
