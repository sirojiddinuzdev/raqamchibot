"""
Yordamchi funksiyalar — kanal tekshirish, klaviatura, va b.
"""
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)


async def check_user_subscribed(bot: Bot, user_id: int, channels: list[dict]) -> list[dict]:
    """
    Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi.
    """
    not_subscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(ch)
        except TelegramError as e:
            logger.warning(f"Kanal tekshirishda xatolik {ch['channel_id']}: {e}")
            not_subscribed.append(ch)
    return not_subscribed


def build_subscribe_keyboard(not_subscribed: list[dict], check_callback: str = "check_sub") -> InlineKeyboardMarkup:
    """Obuna bo'lish uchun inline URL tugmalar (URLlar faqat inline ishlaydi)"""
    buttons = []
    for ch in not_subscribed:
        buttons.append([
            InlineKeyboardButton(
                f"📢 {ch['channel_name']}",
                url=ch["channel_link"]
            )
        ])
    buttons.append([
        InlineKeyboardButton("✅ Obuna bo'ldim", callback_data=check_callback)
    ])
    return InlineKeyboardMarkup(buttons)


# ─── Reply Klaviaturalar (pastda turuvchi tugmalar) ───────────

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Foydalanuvchi asosiy menyusi — pastda doim ko'rinadi"""
    return ReplyKeyboardMarkup(
        [
            ["📱 Raqam sotib olish"],
            ["💳 Hisobni to'ldirish", "💰 Hisobim"],
            ["📞 Admin bilan bog'lanish"],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Admin asosiy menyusi — pastda doim ko'rinadi"""
    return ReplyKeyboardMarkup(
        [
            ["📊 Statistika", "👥 Foydalanuvchilar"],
            ["💸 Balans qo'shish", "💸 Balans ayirish"],
            ["🚫 Ban qo'yish", "✅ Banni ochish"],
            ["📢 Kanallar", "🌍 Davlatlar"],
            ["💳 Karta sozlash", "📨 Ommaviy xabar"],
            ["⏳ Kutayotgan to'lovlar"],
            ["🔙 Bosh menyuga"],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def back_to_main_keyboard() -> ReplyKeyboardMarkup:
    """Faqat orqaga tugmasi"""
    return ReplyKeyboardMarkup(
        [["🔙 Bosh menyuga"]],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        [["❌ Bekor qilish"]],
        resize_keyboard=True,
    )


# ─── Inline Klaviaturalar (xabarlarga biriktirilgan) ─────────

def paginated_keyboard(
    items: list[tuple],
    page: int,
    per_page: int = 10,
    prefix: str = "country",
    back_callback: str = "back_main_inline",
) -> InlineKeyboardMarkup:
    """
    Sahifalangan inline tugmalar.
    items: [(callback_data, label), ...]
    """
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]

    buttons = []
    row = []
    for i, (cb, label) in enumerate(page_items):
        row.append(InlineKeyboardButton(label, callback_data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{prefix}_{page - 1}"))
    if end < len(items):
        nav.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{prefix}_{page + 1}"))
    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(buttons)


def back_inline(callback: str = "back_main_inline") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data=callback)]
    ])
