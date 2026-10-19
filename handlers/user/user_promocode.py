from telegram import Update
from telegram.ext import ContextTypes
import database as db
from helpers import cancel_keyboard, main_menu_keyboard
from handlers.user.user_core import _get_lang


async def user_promo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)
    context.user_data["user_action"] = "use_promo"

    prompts = {
        "uz": "🎁 <b>Promokodni kiriting:</b>\n\nAgar sizda maxsus promokod bo'lsa, uni yuboring.",
        "en": "🎁 <b>Enter your promo code:</b>\n\nIf you have a promo code, send it here.",
        "ru": "🎁 <b>Введите промокод:</b>\n\nЕсли у вас есть промокод, отправьте его сюда.",
    }
    await update.message.reply_text(
        prompts.get(lang, prompts["uz"]),
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang)
    )


async def user_promo_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    user_id = update.effective_user.id
    lang = await _get_lang(user_id)

    res = await db.use_promocode(user_id, code)
    from handlers.admin.admin_core import is_admin

    if res["success"]:
        success_msgs = {
            "uz": f"✅ <b>Tabriklaymiz!</b>\n\nSizning hisobingizga <b>{int(res['amount']):,} so'm</b> qo'shildi.",
            "en": f"✅ <b>Congratulations!</b>\n\n<b>{int(res['amount']):,} UZS</b> has been added to your balance.",
            "ru": f"✅ <b>Поздравляем!</b>\n\nНа ваш баланс добавлено <b>{int(res['amount']):,} сум</b>.",
        }
        await update.message.reply_text(
            success_msgs.get(lang, success_msgs["uz"]),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
        )
    else:
        await update.message.reply_text(
            res["msg"],
            reply_markup=main_menu_keyboard(await is_admin(user_id), lang)
        )
    context.user_data.pop("user_action", None)
