import asyncio
from telegram import Update
from telegram.ext import ContextTypes
import html

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
        if action == "set_country_price":
            context.user_data.pop("adm_action", None)
            context.user_data.pop("target_country", None)
            context.user_data.pop("target_country_name", None)
            from handlers.admin.admin_catalog import adm_countries_handler
            await adm_countries_handler(update, context)
            return
            
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
                    f"Ism: {html.escape(u['full_name'])}\n"
                    f"Username: @{u['username']}\n"
                    f"Balans: {int(u['balance']):,} so'm\n"
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
            clean_text = text.replace(",", "").replace(" ", "").replace(".", "")
            amount = float(clean_text)
            uid = context.user_data.get("target_user")
            if not uid:
                raise ValueError
            
            if action == "add_balance":
                await db.update_balance(uid, amount)
                await update.message.reply_text(f"✅ ID {uid} hisobiga {int(amount):,} so'm qo'shildi.", reply_markup=admin_main_keyboard())
            elif action == "sub_balance":
                await db.update_balance(uid, -amount)
                await update.message.reply_text(f"✅ ID {uid} hisobidan {int(amount):,} so'm ayirildi.", reply_markup=admin_main_keyboard())
            elif action == "confirm_deposit":
                await db.update_balance(uid, amount)
                await update.message.reply_text(f"✅ To'lov tasdiqlandi. ID {uid} hisobiga {int(amount):,} so'm qo'shildi.", reply_markup=admin_main_keyboard())
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"✅ <b>Hisobingiz to'ldirildi!</b>\n💰 Qo'shildi: {int(amount):,} so'm",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                
                # Delete buttons from all admins
                dep_id = context.user_data.get("target_dep_id")
                if dep_id and "deposits" in context.bot_data and dep_id in context.bot_data["deposits"]:
                    admin_msgs = context.bot_data["deposits"][dep_id]["admin_msgs"]
                    for admin_id, msg_id in admin_msgs:
                        try:
                            await context.bot.edit_message_caption(
                                chat_id=admin_id,
                                message_id=msg_id,
                                caption=f"✅ Bu to'lov admin {update.effective_user.first_name} (@{update.effective_user.username or 'yoq'}) tomonidan tasdiqlandi.\n💰 Summa: {int(amount):,} so'm."
                            )
                        except Exception:
                            pass
                    del context.bot_data["deposits"][dep_id]

        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri summa kiritildi.", reply_markup=admin_main_keyboard())
        finally:
            if action in ["add_balance", "sub_balance"] or (action == "confirm_deposit" and "ValueError" not in str(locals().values())):
                context.user_data.pop("adm_action", None)
                context.user_data.pop("target_user", None)
                context.user_data.pop("target_dep_id", None)

    elif action == "reject_deposit":
        uid = context.user_data.get("target_user")
        reason = text if text.lower() != "izohsiz" else "Izohsiz"
        await update.message.reply_text(f"❌ To'lov rad etildi. Sabab: {reason}", reply_markup=admin_main_keyboard())
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"❌ <b>Sizning to'lovingiz qabul qilinmadi!</b>\n\nSabab: {reason}",
                parse_mode="HTML"
            )
        except Exception:
            pass
        
        # Delete buttons from all admins
        dep_id = context.user_data.get("target_dep_id")
        if dep_id and "deposits" in context.bot_data and dep_id in context.bot_data["deposits"]:
            admin_msgs = context.bot_data["deposits"][dep_id]["admin_msgs"]
            for admin_id, msg_id in admin_msgs:
                try:
                    await context.bot.edit_message_caption(
                        chat_id=admin_id,
                        message_id=msg_id,
                        caption=f"❌ Bu to'lov admin {update.effective_user.first_name} (@{update.effective_user.username or 'yoq'}) tomonidan rad etildi.\nSabab: {reason}"
                    )
                except Exception:
                    pass
            del context.bot_data["deposits"][dep_id]
        
        context.user_data.pop("adm_action", None)
        context.user_data.pop("target_user", None)
        context.user_data.pop("target_dep_id", None)

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
            clean_text = text.replace(",", "").replace(" ", "").replace(".", "")
            price = int(clean_text)
            c_code = context.user_data.get("target_country")
            c_name = context.user_data.get("target_country_name")
            await db.set_setting(f"country_{c_code}", str(price))
            
            # Asl narxni ham saqlab qo'yamiz (keyinchalik foyda hisoblash uchun)
            api_countries = context.user_data.get("api_countries", {})
            api_price = api_countries.get(c_code)
            if api_price:
                from config import EXCHANGE_RATE
                api_price_uzs = int(float(api_price) * EXCHANGE_RATE)
                await db.set_setting(f"country_{c_code}_original", str(api_price_uzs))
                
            await update.message.reply_text(
                f"✅ <b>{c_name}</b> davlati {price:,} so'm narxda sotuvga qo'shildi.",
                parse_mode="HTML",
                reply_markup=admin_main_keyboard()
            )
            
            context.user_data.pop("adm_action", None)
            context.user_data.pop("target_country", None)
            context.user_data.pop("target_country_name", None)
            
            # Orqaga asosi menyuga emas, davlatlar ro'yxatiga qaytaramiz
            from handlers.admin.admin_catalog import adm_countries_handler
            await adm_countries_handler(update, context)
            
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri narx kiritildi.", reply_markup=admin_main_keyboard())
            context.user_data.pop("adm_action", None)
            context.user_data.pop("target_country", None)
            context.user_data.pop("target_country_name", None)

    elif action == "add_promo":
        try:
            parts = update.message.text.split()
            if len(parts) == 3:
                code = parts[0].upper()
                amount = float(parts[1])
                max_uses = int(parts[2])
            elif len(parts) == 2:
                import string, random
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                amount = float(parts[0])
                max_uses = int(parts[1])
            else:
                await update.message.reply_text("❌ Noto'g'ri format.", reply_markup=admin_main_keyboard())
                return
                
            await db.create_promocode(code, amount, max_uses)
            await update.message.reply_text(
                f"✅ <b>Promokod yaratildi!</b>\n\n"
                f"🔖 Kod: <code>{code}</code>\n"
                f"💰 Summa: {int(amount):,} so'm\n"
                f"👥 Foydalanishlar soni: {max_uses} marta",
                parse_mode="HTML",
                reply_markup=admin_main_keyboard()
            )
            context.user_data.pop("adm_action", None)
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}", reply_markup=admin_main_keyboard())
            context.user_data.pop("adm_action", None)

    elif action == "add_admin":
        try:
            aid = int(text.strip())
            
            val = await db.get_setting("dynamic_admins")
            admins = [int(x) for x in val.split(",") if x.strip()] if val else []
            
            if aid in ADMIN_IDS or aid in admins:
                await update.message.reply_text("❌ Ushbu foydalanuvchi allaqachon admin.", reply_markup=admin_main_keyboard())
            else:
                admins.append(aid)
                new_val = ",".join(map(str, admins))
                await db.set_setting("dynamic_admins", new_val)
                
                # Try sending message to new admin
                try:
                    await context.bot.send_message(
                        chat_id=aid,
                        text="🎉 Siz botga admin qilib tayinlandingiz! Bosh menyuni ochish uchun /start ni bosing."
                    )
                except Exception:
                    pass
                
                await update.message.reply_text(f"✅ ID {aid} admin qilib tayinlandi.", reply_markup=admin_main_keyboard())
        except ValueError:
            await update.message.reply_text("❌ ID raqam bo'lishi kerak.", reply_markup=admin_main_keyboard())
            
        context.user_data.pop("adm_action", None)
