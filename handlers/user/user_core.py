import logging
from telegram import Update
from telegram.ext import ContextTypes

import database as db
from helpers import (
    check_user_subscribed,
    build_subscribe_keyboard,
    main_menu_keyboard,
)
from handlers.admin.admin_core import is_admin

logger = logging.getLogger(__name__)


async def ensure_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """False qaytarsa — obuna bo'lmagan"""
    user_id = update.effective_user.id
    channels = await db.get_channels()
    if not channels:
        return True
    not_subs = await check_user_subscribed(context.bot, user_id, channels)
    if not_subs:
        kbd = build_subscribe_keyboard(not_subs, "check_sub")
        text = (
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            + "\n".join(f"• {ch['channel_name']}" for ch in not_subs)
        )
        msg = update.message or (update.callback_query.message if update.callback_query else None)
        if msg:
            await msg.reply_text(text, parse_mode="HTML", reply_markup=kbd)
    return not not_subs


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    ref_id = None
    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id == user_id:
                ref_id = None
        except ValueError:
            pass

    existing = await db.get_user(user_id)
    if not existing:
        await db.create_user(
            user_id=user_id,
            username=user.username or "",
            full_name=user.full_name or "",
            referred_by=ref_id
        )

    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        await update.message.reply_text("🚫 Siz botdan bloklangansiz.")
        return

    balance = user_data["balance"] if user_data else 0.0
    text = (
        f"👋 <b>Xush kelibsiz, {user.first_name}!</b>\n\n"
        f"🤖 <b>Raqamchi Bot</b> — Telegram akkount raqamlari sotib olish xizmati\n\n"
        f"💰 <b>Hisobingiz:</b> {int(balance):,} so'm\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"👇 Quyidagi menyudan foydalaning:"
    )
    is_admin_user = await is_admin(user_id)
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin_user)
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    channels = await db.get_channels()
    not_subs = await check_user_subscribed(context.bot, user_id, channels)

    if not_subs:
        kbd = build_subscribe_keyboard(not_subs, "check_sub")
        await query.message.edit_text(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!\n\n"
            + "\n".join(f"• {ch['channel_name']}" for ch in not_subs),
            parse_mode="HTML",
            reply_markup=kbd
        )
    else:
        user_data = await db.get_user(user_id)
        balance = user_data["balance"] if user_data else 0.0
        await query.message.delete()
        await query.message.chat.send_message(
            f"✅ <b>Obuna tasdiqlandi!</b>\n\n"
            f"👋 Xush kelibsiz, <b>{query.from_user.first_name}</b>!\n\n"
            f"💰 <b>Hisobingiz:</b> {int(balance):,} so'm\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(await is_admin(user_id))
        )


async def back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'🔙 Bosh menyuga' tugmasi"""
    user_id = update.effective_user.id
    context.user_data.clear()

    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if user_data and user_data["is_banned"]:
        await update.message.reply_text("🚫 Siz bloklangansiz.")
        return

    balance = user_data["balance"] if user_data else 0.0
    await update.message.reply_text(
        f"🏠 <b>Bosh menyu</b>\n\n"
        f"💰 <b>Hisobingiz:</b> {int(balance):,} so'm\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(user_id))
    )


async def my_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'💰 Hisobim' tugmasi"""
    user_id = update.effective_user.id

    if not await ensure_subscribed(update, context):
        return

    user_data = await db.get_user(user_id)
    if not user_data:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi.")
        return

    purchases = await db.get_user_purchases(user_id)
    purchase_text = ""
    if purchases:
        purchase_text = "\n\n📋 <b>Oxirgi xaridlaringiz:</b>\n"
        for p in purchases[:5]:
            status_icon = "✅" if p["status"] == "completed" else "⏳"
            purchase_text += (
                f"{status_icon} {p['country_name']} — "
                f"<code>{p['number']}</code> — {int(p['price']):,} so'm\n"
            )

    text = (
        f"💰 <b>Hisobim</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Ism: {user_data['full_name']}\n"
        f"💵 Balans: <b>{int(user_data['balance']):,} so'm</b>\n"
        f"📅 Qo'shilgan: {user_data['joined_at'][:10]}"
        + purchase_text
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(await is_admin(user_id))
    )


async def contact_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'📞 Admin bilan bog'lanish' tugmasi"""
    if not await ensure_subscribed(update, context):
        return

    from config import SUPPORT_LINK
    await update.message.reply_text(
        f"📞 <b>Admin bilan bog'lanish</b>\n\n"
        f"Har qanday savol yoki muammo uchun:\n"
        f"👉 {SUPPORT_LINK}",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(await is_admin(update.effective_user.id))
    )
