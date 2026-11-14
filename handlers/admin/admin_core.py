import html

from telegram import Update
from telegram.ext import ContextTypes
from psycopg.rows import dict_row

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

    for key in list(context.user_data.keys()):
        if key != "admin_panel":
            context.user_data.pop(key, None)
    context.user_data["admin_panel"] = True
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

    async with db.get_connection() as dbase:
        async with dbase.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT country, SUM(price) as tot, COUNT(*) as c "
                "FROM purchases WHERE status='completed' "
                "GROUP BY country, country_name"
            )
            rows = await cur.fetchall()

    if rows:
        from countries import get_country_name
        top_countries = sorted(
            rows,
            key=lambda row: (-row["c"], row["country"]),
        )[:3]
        top_countries_text = "\n".join(
            f"{index}. {get_country_name(row['country'])} — <b>{row['c']}</b> marta"
            for index, row in enumerate(top_countries, start=1)
        )

        for r in rows:
            c = r["country"]
            count = r["c"]
            tot = r["tot"]

            completed_purchases += count
            total_income += tot

            orig = await db.get_setting(f"country_{c}_original")
            if orig:
                total_original += (float(orig) * count)
    else:
        top_countries_text = "Yo'q"

    profit = total_income - total_original

    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total_users}</b>\n"
        f"✅ Sotilgan raqamlar: <b>{completed_purchases}</b> ta\n"
        f"👑 <b>Eng ko'p sotilgan 3 ta davlat:</b>\n{top_countries_text}\n"
        f"💵 Asl narxi (Tan narxi): <b>{int(total_original):,} so'm</b>\n"
        f"💰 Biz sotgan narx: <b>{int(total_income):,} so'm</b>\n"
        f"📈 Sof foyda: <b>{int(profit):,} so'm</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def adm_referral_stats_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    total_referrals, leaderboard = await db.get_admin_referral_stats()
    lines = []
    for rank, referrer in enumerate(leaderboard, start=1):
        display_name = (
            f'@{referrer["username"]}'
            if referrer["username"]
            else referrer["full_name"] or str(referrer["user_id"])
        )
        safe_name = html.escape(display_name)
        lines.append(
            f'{rank}. <a href="tg://user?id={referrer["user_id"]}">'
            f'{safe_name}</a> (ID: <code>{referrer["user_id"]}</code>) — '
            f'<b>{referrer["referrals"]}</b> ta'
        )

    text = (
        "🏆 <b>Referral statistikasi</b>\n\n"
        f"👥 Referral orqali qo'shilganlar: <b>{total_referrals}</b> ta\n\n"
        "🔝 <b>Eng ko'p odam taklif qilgan Top 10:</b>\n"
        + ("\n".join(lines) if lines else "Hozircha referral yo'q.")
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
