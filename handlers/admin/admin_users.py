from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import html

import database as db
from helpers import cancel_keyboard
from handlers.admin.admin_core import is_admin
from telegram import ReplyKeyboardMarkup


async def adm_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👥 Foydalanuvchilar (qidirish/ro'yxat)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    # Avval searchni yoqib qo'yamiz va keyboardni cancel qilib qo'yamiz
    context.user_data["adm_action"] = "search_user"
    await update.message.reply_text("Foydalanuvchi qidirish faollashtirildi. Bekor qilish uchun tugmani bosing:", reply_markup=cancel_keyboard())
    
    # Keyin inline tugmali ro'yxatni yuboramiz
    await _send_users_page(update, context, page=0)


async def _send_users_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    per_page = 10
    total = await db.get_users_count()
    users = await db.get_users_page(limit=per_page, offset=page * per_page)
    
    text = f"👥 <b>Foydalanuvchilar (Jami: {total}):</b>\nSahifa: {page+1}\n\n"
    for u in users:
        status = "🚫" if u["is_banned"] else "✅"
        text += f"{status} <code>{u['user_id']}</code> — {html.escape(u['full_name'])} — {int(u['balance']):,} so'm\n"
        
    text += "\nBiror foydalanuvchi ID sini pastga kiriting (balans, ban boshqaruvi uchun):"

    kbd = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"adm_users_page_{page-1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"adm_users_page_{page+1}"))
    
    if nav:
        kbd.append(nav)
    
    markup = InlineKeyboardMarkup(kbd) if kbd else None
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=markup)


async def adm_users_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar ro'yxatida sahifa o'zgartirish"""
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split("_")[-1])
    await _send_users_page(update, context, page)


async def adm_ban_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban menyusi"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return
    
    kbd = ReplyKeyboardMarkup([
        ["🚫 Ban qo'yish", "✅ Banni ochish"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)
    await update.message.reply_text("🚫 BAN menyusi:", reply_markup=kbd)

async def adm_balance_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Balans menyusi"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return
    
    kbd = ReplyKeyboardMarkup([
        ["💸 Balans qo'shish", "💸 Balans ayirish"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)
    await update.message.reply_text("💰 Balans boshqaruvi:", reply_markup=kbd)

async def prompt_user_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi qidirish / ban / balans uchun umumniy handler"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return
    context.user_data["adm_action"] = "search_user"
    await update.message.reply_text("Foydalanuvchi ID sini kiriting:", reply_markup=cancel_keyboard())


async def adm_add_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchiga balans qo'shish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = query.data.split("_")[-1]
    context.user_data["adm_action"] = "add_balance"
    context.user_data["target_user"] = int(uid)
    await query.message.reply_text(f"ID {uid} uchun qo'shmoqchi bo'lgan summani so'mda kiriting:", reply_markup=cancel_keyboard())


async def adm_sub_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchidan balans ayirish tugmasi"""
    query = update.callback_query
    await query.answer()
    uid = query.data.split("_")[-1]
    context.user_data["adm_action"] = "sub_balance"
    context.user_data["target_user"] = int(uid)
    await query.message.reply_text(f"ID {uid} dan ayirmoqchi bo'lgan summani so'mda kiriting:", reply_markup=cancel_keyboard())


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
