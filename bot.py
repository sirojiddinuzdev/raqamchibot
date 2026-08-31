"""
Raqamchi Bot — Asosiy fayl
Python-telegram-bot v22 (PTB) kutubxonasi
"""
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, ADMIN_IDS
import database as db
from handlers.user import (
    start_handler,
    check_subscription_callback,
    back_to_main_handler,
    my_balance_handler,
    contact_admin_handler,
    deposit_handler,
    buy_number_handler,
    country_page_callback,
    select_country_callback,
    cancel_buy_callback,
    confirm_buy_callback,
    get_code_callback,
    cancel_deposit_callback,
)
from handlers.user.user_promocode import user_promo_handler
from handlers.admin import (
    admin_panel,
    adm_stats_handler,
    adm_users_handler,
    adm_add_balance_handler,
    adm_sub_balance_handler,
    adm_ban_handler,
    adm_unban_handler,
    prompt_user_id_handler,
    adm_ban_menu_handler,
    adm_balance_menu_handler,
    adm_users_page_callback,
    adm_channels_handler,
    adm_add_channel_callback,
    adm_remove_channel_callback,
    adm_del_channel_callback,
    adm_countries_handler,
    adm_add_country_list_callback,
    adm_edit_country_list_callback,
    adm_clist_page_callback,
    adm_pick_country_callback,
    adm_remove_country_list_callback,
    adm_del_country_callback,
    adm_back_to_catalog_callback,
    adm_set_card_handler,
    adm_broadcast_handler,
    adm_pending_deps_handler,
    adm_confirm_dep_callback,
    adm_reject_dep_callback,
    adm_admins_handler,
    adm_add_admin_callback,
    adm_remove_admin_callback,
    adm_del_admin_callback,
)
from handlers.admin.admin_promocodes import (
    adm_promocodes_handler,
    adm_add_promo_callback,
    adm_del_promo_callback,
    adm_del_promo_confirm_callback,
    adm_promo_back_callback,
)

# Logging
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# ─── Admin komandasi ──────────────────────────────────────────

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel(update, context)


# ─── Asosiy text handler (holatlarni boshqarish uchun) ────────

async def universal_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Matn handlerlarini to'g'ri yo'naltirish"""
    user_id = update.effective_user.id

    from handlers.admin.admin_core import is_admin
    # Admin action lari uchun
    if await is_admin(user_id):
        adm_action = context.user_data.get("adm_action", "")
        if adm_action:
            # Bekor qilish tugmasi admin amali uchun
            if update.message.text == "❌ Bekor qilish":
                context.user_data.clear()
                from helpers import admin_main_keyboard
                await update.message.reply_text("Bekor qilindi.", reply_markup=admin_main_keyboard())
                return
            from handlers.admin import admin_text_handler
            await admin_text_handler(update, context)
            return

    # Foydalanuvchi summa kiritayotganda
    if context.user_data.get("awaiting_deposit_amount"):
        if update.message.text == "❌ Bekor qilish":
            context.user_data.clear()
            await back_to_main_handler(update, context)
            return
        
        try:
            amount_text = update.message.text.replace(" ", "").replace(",", "").replace(".", "")
            amount = int(amount_text)
            if amount < 1000:
                await update.message.reply_text("❌ Eng kam to'lov summasi 1,000 so'm.")
                return
            context.user_data["deposit_amount"] = amount
            context.user_data.pop("awaiting_deposit_amount", None)
            
            # Endi rasm so'rash
            from handlers.user.user_deposit import start_deposit_process
            await start_deposit_process(update, context)
            return
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri summa kiritildi. Iltimos, faqat raqamlardan foydalaning.")
            return

    # Foydalanuvchi chek yuborish holatida
    if context.user_data.get("awaiting_deposit_check"):
        if update.message.text == "❌ Bekor qilish":
            context.user_data.clear()
            await back_to_main_handler(update, context)
            return
            
        await update.message.reply_text(
            "📸 Iltimos, chek <b>rasmini</b> yoki faylini yuboring.",
            parse_mode="HTML"
        )
        return

    # Foydalanuvchi promo kod kiritishi
    user_action = context.user_data.get("user_action")
    if user_action == "use_promo":
        if update.message.text == "❌ Bekor qilish":
            context.user_data.clear()
            await back_to_main_handler(update, context)
            return
        from handlers.user.user_promocode import user_promo_text_handler
        await user_promo_text_handler(update, context)
        return


async def universal_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media (rasm/video/ovozli) handler"""
    user_id = update.effective_user.id
    
    # Chek kutilayotgan bo'lsa
    if context.user_data.get("awaiting_deposit_check"):
        if update.message.photo or update.message.document:
            from handlers.user.user_deposit import deposit_check_handler
            await deposit_check_handler(update, context)
        else:
            await update.message.reply_text("❌ Iltimos, to'lov chekini rasm yoki fayl ko'rinishida yuboring.")
        return
        
    # Agar admin xabar yozish holatida bo'lsa
    adm_action = context.user_data.get("adm_action")
    if adm_action:
        if adm_action == "broadcast":
            from handlers.admin.admin_text_handler import admin_text_handler
            await admin_text_handler(update, context)
        else:
            await update.message.reply_text("❌ Iltimos, faqat matn yuboring.")
        return
        
    # Agar foydalanuvchi summa kiritishi kerak bo'lsa
    if context.user_data.get("awaiting_deposit_amount"):
        await update.message.reply_text("❌ Iltimos, summani matn ko'rinishida raqamlar bilan yuboring.")
        return
        
    # Agar foydalanuvchi promo kod kiritishi kerak bo'lsa
    if context.user_data.get("user_action") == "use_promo":
        await update.message.reply_text("❌ Iltimos, promokodni matn ko'rinishida yuboring.")
        return


# ─── Bot buyruqlarini sozlash ─────────────────────────────────

async def post_init(application: Application):
    await db.init_db()
    logger.info("✅ Ma'lumotlar bazasi ishga tushdi")

    commands = [
        BotCommand("start", "Botni ishga tushirish"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot buyruqlari o'rnatildi")


# ─── Asosiy funksiya ──────────────────────────────────────────

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Buyruqlar ──
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.Regex("^(👨‍💻 Admin Panel|🔙 Orqaga)$"), admin_command))

    # ── Reply Keyboard matnlari (Foydalanuvchi) ──
    from handlers.user.user_core import chat_join_request_handler
    app.add_handler(ChatJoinRequestHandler(chat_join_request_handler))

    app.add_handler(MessageHandler(filters.Regex("^📱 Raqam sotib olish$"), buy_number_handler))
    app.add_handler(MessageHandler(filters.Regex("^💳 Hisobni to'ldirish$"), deposit_handler))
    app.add_handler(MessageHandler(filters.Regex("^💰 Hisobim$"), my_balance_handler))
    app.add_handler(MessageHandler(filters.Regex("^📞 Admin bilan bog'lanish$"), contact_admin_handler))
    app.add_handler(MessageHandler(filters.Regex("^🔙 Bosh menyuga$"), back_to_main_handler))
    app.add_handler(MessageHandler(filters.Regex("^🎁 Promokod$"), user_promo_handler))

    # ── Reply Keyboard matnlari (Admin) ──
    app.add_handler(MessageHandler(filters.Regex("^📊 Statistika$"), adm_stats_handler))
    app.add_handler(MessageHandler(filters.Regex("^👥 Foydalanuvchilar$"), adm_users_handler))
    app.add_handler(MessageHandler(filters.Regex("^🚫 BAN ✅$"), adm_ban_menu_handler))
    app.add_handler(MessageHandler(filters.Regex("^➖ Balans ➕$"), adm_balance_menu_handler))
    app.add_handler(MessageHandler(
        filters.Regex("^(💸 Balans qo'shish|💸 Balans ayirish|🚫 Ban qo'yish|✅ Banni ochish)$"), 
        prompt_user_id_handler
    ))
    app.add_handler(MessageHandler(filters.Regex("^📢 Kanallar$"), adm_channels_handler))
    app.add_handler(MessageHandler(filters.Regex("^🌍 Davlatlar$"), adm_countries_handler))
    app.add_handler(MessageHandler(filters.Regex("^💳 Karta sozlash$"), adm_set_card_handler))
    app.add_handler(MessageHandler(filters.Regex("^📨 Ommaviy xabar$"), adm_broadcast_handler))
    app.add_handler(MessageHandler(filters.Regex("^⏳ Kutayotgan to'lovlar$"), adm_pending_deps_handler))
    app.add_handler(MessageHandler(filters.Regex("^👮‍♂️ Adminlar$"), adm_admins_handler))
    app.add_handler(MessageHandler(filters.Regex("^🎁 Promokodlar$"), adm_promocodes_handler))

    # ── Qolgan Inline Callback lar ──
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(country_page_callback, pattern=r"^page_country_\d+$"))
    app.add_handler(CallbackQueryHandler(select_country_callback, pattern=r"^select_country_"))
    app.add_handler(CallbackQueryHandler(cancel_buy_callback, pattern="^cancel_buy$"))
    app.add_handler(CallbackQueryHandler(confirm_buy_callback, pattern="^confirm_buy$"))
    app.add_handler(CallbackQueryHandler(get_code_callback, pattern=r"^get_code_"))
    app.add_handler(CallbackQueryHandler(cancel_deposit_callback, pattern="^cancel_deposit$"))
    app.add_handler(CallbackQueryHandler(adm_users_page_callback, pattern=r"^adm_users_page_\d+$"))

    app.add_handler(CallbackQueryHandler(adm_add_balance_handler, pattern=r"^adm_add_bal_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_sub_balance_handler, pattern=r"^adm_sub_bal_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_ban_handler, pattern=r"^adm_ban_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_unban_handler, pattern=r"^adm_unban_\d+$"))

    app.add_handler(CallbackQueryHandler(adm_add_channel_callback, pattern="^adm_add_channel$"))
    app.add_handler(CallbackQueryHandler(adm_remove_channel_callback, pattern="^adm_remove_channel$"))
    app.add_handler(CallbackQueryHandler(adm_del_channel_callback, pattern=r"^adm_del_ch_"))
    app.add_handler(CallbackQueryHandler(adm_add_country_list_callback, pattern="^adm_add_country_list$"))
    app.add_handler(CallbackQueryHandler(adm_edit_country_list_callback, pattern="^adm_edit_country_list$"))
    app.add_handler(CallbackQueryHandler(adm_clist_page_callback, pattern=r"^page_adm_clist_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_pick_country_callback, pattern=r"^adm_pick_country_"))
    app.add_handler(CallbackQueryHandler(adm_remove_country_list_callback, pattern="^adm_remove_country_list$"))
    app.add_handler(CallbackQueryHandler(adm_del_country_callback, pattern=r"^adm_del_country_"))
    app.add_handler(CallbackQueryHandler(adm_back_to_catalog_callback, pattern="^adm_back_to_catalog$"))
    app.add_handler(CallbackQueryHandler(adm_confirm_dep_callback, pattern=r"^confirm_dep_"))
    app.add_handler(CallbackQueryHandler(adm_reject_dep_callback, pattern=r"^reject_dep_"))
    app.add_handler(CallbackQueryHandler(adm_add_admin_callback, pattern="^adm_add_admin$"))
    app.add_handler(CallbackQueryHandler(adm_remove_admin_callback, pattern="^adm_remove_admin$"))
    app.add_handler(CallbackQueryHandler(adm_del_admin_callback, pattern=r"^adm_del_adm_\d+$"))
    
    app.add_handler(CallbackQueryHandler(adm_add_promo_callback, pattern="^adm_add_promo$"))
    app.add_handler(CallbackQueryHandler(adm_del_promo_callback, pattern="^adm_del_promo$"))
    app.add_handler(CallbackQueryHandler(adm_del_promo_confirm_callback, pattern=r"^adm_del_promo_"))
    app.add_handler(CallbackQueryHandler(adm_promo_back_callback, pattern="^adm_promo_back$"))

    # ── Matn va media kiritish uchun handlerlar ──
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        universal_text_handler
    ))
    app.add_handler(MessageHandler(
        ~filters.TEXT & ~filters.COMMAND,
        universal_media_handler
    ))

    logger.info("🤖 Raqamchi Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
