from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import database as db
from handlers.admin.admin_core import is_admin
from helpers import cancel_keyboard, admin_main_keyboard

async def adm_promocodes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    codes = await db.get_all_promocodes()
    text = "🎁 <b>Promokodlar boshqaruvi</b>\n\n"
    if codes:
        for c in codes:
            text += f"🔖 <code>{c['code']}</code> - {int(c['amount']):,} so'm ({c['uses']}/{c['max_uses']})\n"
    else:
        text += "Hozircha promokodlar yo'q.\n"

    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi promokod qo'shish", callback_data="adm_add_promo")],
        [InlineKeyboardButton("❌ Promokodni o'chirish", callback_data="adm_del_promo")]
    ])
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kbd)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kbd)

async def adm_add_promo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["adm_action"] = "add_promo"
    await query.message.edit_text(
        "➕ <b>Yangi promokod qo'shish</b>\n\n"
        "Promokod ma'lumotlarini quyidagi formatda kiriting:\n"
        "<code>KOD SUMMA SONI</code>\n\n"
        "Masalan: <code>START2024 5000 100</code>\n"
        "(Bu START2024 kodini 5000 so'mlik 100 kishiga beradi)\n\n"
        "Yoki kodni avtomatik generatsiya qilish uchun faqat <code>SUMMA SONI</code> kiriting:\n"
        "Masalan: <code>5000 10</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="adm_promo_back")]])
    )

async def adm_del_promo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    codes = await db.get_all_promocodes()
    if not codes:
        await query.message.edit_text("❌ O'chirish uchun promokodlar yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="adm_promo_back")]]))
        return
        
    kbd_buttons = []
    for c in codes:
        kbd_buttons.append([InlineKeyboardButton(f"❌ {c['code']}", callback_data=f"adm_del_promo_{c['code']}")])
        
    kbd_buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="adm_promo_back")])
    await query.message.edit_text("❌ O'chirmoqchi bo'lgan promokodni tanlang:", reply_markup=InlineKeyboardMarkup(kbd_buttons))

async def adm_del_promo_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("adm_del_promo_", "")
    
    await db.delete_promocode(code)
    await query.message.edit_text(f"✅ Promokod <b>{code}</b> o'chirildi.", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="adm_promo_back")]]))

async def adm_promo_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("adm_action", None)
    await adm_promocodes_handler(update, context)
