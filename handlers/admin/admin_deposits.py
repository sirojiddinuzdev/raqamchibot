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

    # callback_data = "confirm_dep_USERID"
    uid = query.data.replace("confirm_dep_", "")

    context.user_data["adm_action"] = "confirm_deposit"
    context.user_data["target_user"] = int(uid)

    await query.message.reply_text(
        f"✅ Kiritmoqchi bo'lgan summani yozing (ID: {uid}):\n(Masalan: 5 yoki 5.5)",
        reply_markup=cancel_keyboard()
    )
