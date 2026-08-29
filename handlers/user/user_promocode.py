from telegram import Update
from telegram.ext import ContextTypes
import database as db
from helpers import cancel_keyboard, main_menu_keyboard

async def user_promo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["user_action"] = "use_promo"
    await update.message.reply_text(
        "🎁 <b>Promokodni kiriting:</b>\n\n"
        "Agar sizda maxsus promokod bo'lsa, uni yuboring.",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def user_promo_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    user_id = update.effective_user.id
    
    res = await db.use_promocode(user_id, code)
    from handlers.admin.admin_core import is_admin
    
    if res["success"]:
        await update.message.reply_text(
            f"✅ <b>Tabriklaymiz!</b>\n\n"
            f"Sizning hisobingizga <b>{int(res['amount']):,} so'm</b> qo'shildi.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(await is_admin(user_id))
        )
    else:
        await update.message.reply_text(
            res["msg"],
            reply_markup=main_menu_keyboard(await is_admin(user_id))
        )
    context.user_data.pop("user_action", None)
