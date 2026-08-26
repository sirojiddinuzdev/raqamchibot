from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from helpers import cancel_keyboard
from handlers.admin.admin_core import is_admin


async def adm_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👥 Foydalanuvchilar (qidirish/ro'yxat)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

async def prompt_user_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi qidirish / ban / balans uchun umumniy handler"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return
    context.user_data["adm_action"] = "search_user"
    await update.message.reply_text("Foydalanuvchi ID sini kiriting:", reply_markup=cancel_keyboard())

    # Eng oxirgi 10 ta foydalanuvchini ko'rsatamiz
    users = await db.get_all_users()
    users.reverse()
    recent = users[:10]

    text = "👥 <b>Oxirgi qo'shilgan 10 ta foydalanuvchi:</b>\n\n"
    for u in recent:
        status = "🚫 (Ban)" if u["is_banned"] else "✅"
        text += f"{status} <code>{u['user_id']}</code> — {u['full_name']} — {u['balance']}$\n"

    text += "\nBiror foydalanuvchi ID sini pastga kiriting (balans, ban boshqaruvi uchun):"
    context.user_data["adm_action"] = "search_user"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=cancel_keyboard())


async def adm_add_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchiga balans qo'shish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = query.data.split("_")[-1]
    context.user_data["adm_action"] = "add_balance"
    context.user_data["target_user"] = int(uid)
    await query.message.reply_text(f"ID {uid} uchun qo'shmoqchi bo'lgan summani kiriting ($):", reply_markup=cancel_keyboard())


async def adm_sub_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchidan balans ayirish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = query.data.split("_")[-1]
    context.user_data["adm_action"] = "sub_balance"
    context.user_data["target_user"] = int(uid)
    await query.message.reply_text(f"ID {uid} dan ayirmoqchi bo'lgan summani kiriting ($):", reply_markup=cancel_keyboard())


async def adm_ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban qilish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = int(query.data.split("_")[-1])

    await db.ban_user(uid, True)
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ ID {uid} bloklandi.")


async def adm_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bandan yechish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = int(query.data.split("_")[-1])

    await db.ban_user(uid, False)
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ ID {uid} blokdan chiqarildi.")
