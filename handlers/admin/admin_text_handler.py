import asyncio
from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_IDS
from helpers import admin_main_keyboard,cancel_keyboard
from handlers.admin.admin_core import is_admin


async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminning turli inputlarini qabul qilish"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        return

    action = context.user_data.get("adm_action")
    if not action:
        return

    text = update.message.text

    if text == "❌ Bekor qilish":
        context.user_data.pop("adm_action", None)
        await update.message.reply_text("Bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    if action == "broadcast":
        # Xabarni barchaga jo'natish
        users = await db.get_all_users()
        sent = 0
        await update.message.reply_text(f"⏳ Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")
        for u in users:
            try:
                await update.message.copy(u["user_id"])
                sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        await update.message.reply_text(f"✅ Xabar {sent} ta foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=admin_main_keyboard())
        context.user_data.pop("adm_action", None)

    elif action == "search_user":
        try:
            uid = int(text)
            u = await db.get_user(uid)
            if u:
                status = "🚫 Bloklangan" if u["is_banned"] else "✅ Faol"
                msg = (
                    f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
                    f"ID: <code>{u['user_id']}</code>\n"
                    f"Ism: {u['full_name']}\n"
                    f"Username: @{u['username']}\n"
                    f"Balans: {u['balance']}$\n"
                    f"Status: {status}\n"
                )
                from telegram import InlineKeyboardMarkup, InlineKeyboardButton
                kbd = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Balans qo'shish", callback_data=f"adm_add_bal_{uid}"),
                     InlineKeyboardButton("➖ Balans ayirish", callback_data=f"adm_sub_bal_{uid}")],
                    [InlineKeyboardButton("🚫 Ban qilish", callback_data=f"adm_ban_{uid}"),
                     InlineKeyboardButton("✅ Bandan yechish", callback_data=f"adm_unban_{uid}")]
                ])
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=kbd)
            else:
                await update.message.reply_text("❌ Bunday ID topilmadi.", reply_markup=admin_main_keyboard())
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.", reply_markup=admin_main_keyboard())
        context.user_data.pop("adm_action", None)

    elif action in ["add_balance", "sub_balance", "confirm_deposit"]:
        try:
            amount = float(text.replace(",", "."))
            uid = context.user_data.get("target_user")
            if not uid:
                raise ValueError
            
            if action == "add_balance":
                await db.update_balance(uid, amount)
                await update.message.reply_text(f"✅ ID {uid} hisobiga {amount}$ qo'shildi.", reply_markup=admin_main_keyboard())
            elif action == "sub_balance":
                await db.update_balance(uid, -amount)
                await update.message.reply_text(f"✅ ID {uid} hisobidan {amount}$ ayirildi.", reply_markup=admin_main_keyboard())
            elif action == "confirm_deposit":
                await db.update_balance(uid, amount)
                await update.message.reply_text(f"✅ To'lov tasdiqlandi. ID {uid} hisobiga {amount}$ qo'shildi.", reply_markup=admin_main_keyboard())
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"✅ <b>Hisobingiz to'ldirildi!</b>\n💰 Qo'shildi: {amount} $",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri summa kiritildi.", reply_markup=admin_main_keyboard())
        finally:
            context.user_data.pop("adm_action", None)
            context.user_data.pop("target_user", None)

    elif action == "add_channel":
        context.user_data["temp_channel_id"] = text
        context.user_data["adm_action"] = "add_channel_name"
        await update.message.reply_text("Kanalning ko'rinadigan nomini kiriting (masalan: Asosiy kanal):", reply_markup=cancel_keyboard())

    elif action == "add_channel_name":
        context.user_data["temp_channel_name"] = text
        context.user_data["adm_action"] = "add_channel_link"
        await update.message.reply_text("Kanalning havolasini (linkini) kiriting (masalan: https://t.me/kanal):", reply_markup=cancel_keyboard())

    elif action == "add_channel_link":
        channel_id = context.user_data.get("temp_channel_id")
        channel_name = context.user_data.get("temp_channel_name")
        channel_link = text
        await db.add_channel(channel_id, channel_name, channel_link)
        await update.message.reply_text("✅ Kanal qo'shildi.", reply_markup=admin_main_keyboard())
        context.user_data.pop("adm_action", None)
        context.user_data.pop("temp_channel_id", None)
        context.user_data.pop("temp_channel_name", None)

    elif action == "set_card_number":
        context.user_data["temp_card_number"] = text
        context.user_data["adm_action"] = "set_card_owner"
        await update.message.reply_text("Karta egasining ism-familiyasini kiriting:", reply_markup=cancel_keyboard())

    elif action == "set_card_owner":
        card_number = context.user_data.get("temp_card_number")
        card_owner = text
        await db.set_setting("card_number", card_number)
        await db.set_setting("card_owner", card_owner)
        await update.message.reply_text("✅ Karta ma'lumotlari saqlandi.", reply_markup=admin_main_keyboard())
        context.user_data.pop("adm_action", None)
        context.user_data.pop("temp_card_number", None)

    elif action == "set_country_price":
        try:
            price = float(text)
            c_code = context.user_data.get("target_country")
            c_name = context.user_data.get("target_country_name")
            await db.set_setting(f"country_{c_code}", str(price))
            await update.message.reply_text(f"✅ <b>{c_name}</b> davlati {price}$ narxda sotuvga qo'shildi.", parse_mode="HTML", reply_markup=admin_main_keyboard())
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri narx kiritildi.", reply_markup=admin_main_keyboard())
        context.user_data.pop("adm_action", None)
        context.user_data.pop("target_country", None)
        context.user_data.pop("target_country_name", None)
