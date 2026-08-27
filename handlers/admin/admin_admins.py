from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from helpers import cancel_keyboard
from handlers.admin.admin_core import is_admin
from config import ADMIN_IDS

async def adm_admins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👮‍♂️ Adminlar menyusi"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    val = await db.get_setting("dynamic_admins")
    admins = [int(x) for x in val.split(",") if x.strip()] if val else []

    text = "👮‍♂️ <b>Joriy adminlar ro'yxati:</b>\n\n"
    for i, aid in enumerate(admins, 1):
        u = await db.get_user(aid)
        name = u["full_name"] if u else "Noma'lum"
        text += f"{i}. <a href='tg://user?id={aid}'>{name}</a> (<code>{aid}</code>)\n"

    if not admins:
        text += "Qo'shimcha adminlar yo'q.\n"
        
    text += "\n<i>Asosiy adminlar (kod ichida yozilgan) bu yerda ko'rinmaydi.</i>"

    kbd = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Admin qo'shish", callback_data="adm_add_admin")],
        [InlineKeyboardButton("➖ Adminni o'chirish", callback_data="adm_remove_admin")]
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kbd)

async def adm_add_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["adm_action"] = "add_admin"
    await query.message.delete()
    await query.message.chat.send_message(
        "➕ Yangi adminning Telegram ID raqamini kiriting (masalan: 123456789):",
        reply_markup=cancel_keyboard()
    )

async def adm_remove_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    val = await db.get_setting("dynamic_admins")
    admins = [int(x) for x in val.split(",") if x.strip()] if val else []

    if not admins:
        await query.message.edit_text("❌ Qo'shimcha adminlar yo'q.")
        return

    kbd = []
    for aid in admins:
        u = await db.get_user(aid)
        name = u["full_name"] if u else str(aid)
        kbd.append([InlineKeyboardButton(f"❌ {name} ({aid})", callback_data=f"adm_del_adm_{aid}")])

    await query.message.edit_text("➖ O'chirish uchun adminni tanlang:", reply_markup=InlineKeyboardMarkup(kbd))

async def adm_del_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    aid = int(query.data.split("_")[-1])
    
    val = await db.get_setting("dynamic_admins")
    admins = [int(x) for x in val.split(",") if x.strip()] if val else []
    
    if aid in admins:
        admins.remove(aid)
        new_val = ",".join(map(str, admins))
        await db.set_setting("dynamic_admins", new_val)
        await query.message.edit_text(f"✅ ID {aid} adminlar ro'yxatidan o'chirildi.")
    else:
        await query.message.edit_text("❌ Ushbu foydalanuvchi admin emas.")
