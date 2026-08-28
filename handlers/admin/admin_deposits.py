from telegram import Update
from telegram.ext import ContextTypes

import database as db
from handlers.admin.admin_core import is_admin
from helpers import cancel_keyboard


async def adm_pending_deps_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📥 To'lovlar tugmasi (Hozircha faqat stub)"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    await update.message.reply_text("📥 To'lovlar xabarlari avtomatik tarzda bot orqali sizga keladi.")


async def adm_confirm_dep_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminga kelgan to'lov chekini tasdiqlash tugmasi"""
    query = update.callback_query
    await query.answer()

    # callback_data = "confirm_dep_dep_userid_timestamp"
    dep_id = query.data.replace("confirm_dep_", "")
    
    if "deposits" not in context.bot_data or dep_id not in context.bot_data["deposits"]:
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ Bu to'lov xabari eskirgan yoki boshqa admin tomonidan ko'rib chiqilgan.")
        return

    dep_info = context.bot_data["deposits"][dep_id]
    uid = dep_info["user_id"]

    context.user_data["adm_action"] = "confirm_deposit"
    context.user_data["target_user"] = int(uid)
    context.user_data["target_dep_id"] = dep_id

    await query.message.reply_text(
        f"✅ Kiritmoqchi bo'lgan summani so'mda yozing (ID: {uid}):\n(Masalan: 15000)",
        reply_markup=cancel_keyboard()
    )


async def adm_reject_dep_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminga kelgan to'lov chekini rad etish tugmasi"""
    query = update.callback_query
    await query.answer()

    dep_id = query.data.replace("reject_dep_", "")
    
    if "deposits" not in context.bot_data or dep_id not in context.bot_data["deposits"]:
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ Bu to'lov xabari eskirgan yoki boshqa admin tomonidan ko'rib chiqilgan.")
        return

    dep_info = context.bot_data["deposits"][dep_id]
    uid = dep_info["user_id"]

    context.user_data["adm_action"] = "reject_deposit"
    context.user_data["target_user"] = int(uid)
    context.user_data["target_dep_id"] = dep_id

    await query.message.reply_text(
        f"❌ To'lovni rad etish sababini yozing:\n(Agar izohsiz qoldirmoqchi bo'lsangiz 'Izohsiz' deb yozing)",
        reply_markup=cancel_keyboard()
    )
