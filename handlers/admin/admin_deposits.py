from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from handlers.admin.admin_core import is_admin
from helpers import admin_main_keyboard, cancel_keyboard


async def _complete_deposit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    dep_id: str,
    amount: float,
):
    dep_info = context.bot_data["deposits"][dep_id]
    user_id = int(dep_info["user_id"])
    await db.update_balance(user_id, amount)
    await update.callback_query.message.reply_text(
        f"✅ To'lov tasdiqlandi. ID {user_id} hisobiga {int(amount):,} so'm qo'shildi.",
        reply_markup=admin_main_keyboard(),
    )

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>Hisobingiz to'ldirildi!</b>\n💰 Qo'shildi: {int(amount):,} so'm",
            parse_mode="HTML",
        )
    except Exception:
        pass

    for admin_id, message_id in dep_info.get("admin_msgs", []):
        try:
            await context.bot.edit_message_caption(
                chat_id=admin_id,
                message_id=message_id,
                caption=(
                    f"✅ Bu to'lov admin {update.effective_user.first_name} "
                    f"(@{update.effective_user.username or 'yoq'}) tomonidan tasdiqlandi.\n"
                    f"💰 Summa: {int(amount):,} so'm."
                ),
                reply_markup=None,
            )
        except Exception:
            pass

    for admin_id, message_id in dep_info.get("amount_prompt_msgs", []):
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=admin_id,
                message_id=message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    context.bot_data["deposits"].pop(dep_id, None)
    if context.user_data.get("target_dep_id") == dep_id:
        context.user_data.pop("adm_action", None)
        context.user_data.pop("target_user", None)
        context.user_data.pop("target_dep_id", None)

async def adm_confirm_dep_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminga kelgan to'lov chekini tasdiqlash tugmasi"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("Ruxsat yo'q.", show_alert=True)
        return
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

    amount = int(float(dep_info["amount"]))
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"✅ {amount:,} so'mni qo'shish",
            callback_data=f"auto_confirm_dep_{dep_id}",
        )
    ]])
    prompt = await query.message.reply_text(
        f"✅ Kiritmoqchi bo'lgan summani so'mda yozing (ID: {uid}):\n"
        f"(Masalan: 15000)\n\n"
        f"Foydalanuvchi kiritgan summa: {amount:,} so'm",
        reply_markup=keyboard,
    )
    dep_info.setdefault("amount_prompt_msgs", []).append(
        (query.from_user.id, prompt.message_id)
    )


async def adm_auto_confirm_dep_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("Ruxsat yo'q.", show_alert=True)
        return

    dep_id = query.data.removeprefix("auto_confirm_dep_")
    deposits = context.bot_data.get("deposits", {})
    dep_info = deposits.get(dep_id)
    if not dep_info:
        await query.answer("Bu to'lov allaqachon ko'rib chiqilgan.", show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    try:
        amount = float(dep_info["amount"])
    except (TypeError, ValueError):
        await query.answer("To'lov summasi noto'g'ri.", show_alert=True)
        return

    if amount <= 0:
        await query.answer("To'lov summasi noto'g'ri.", show_alert=True)
        return

    await query.answer()
    await _complete_deposit(update, context, dep_id, amount)


async def adm_reject_dep_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminga kelgan to'lov chekini rad etish tugmasi"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("Ruxsat yo'q.", show_alert=True)
        return
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
        "❌ To'lovni rad etish sababini yozing:\n(Agar izohsiz qoldirmoqchi bo'lsangiz 'Izohsiz' deb yozing)",
        reply_markup=cancel_keyboard()
    )
