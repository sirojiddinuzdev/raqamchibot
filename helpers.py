"""
helpers.py — Ko'p tilli klaviaturalar va yordamchi funksiyalar
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
import database as db
from strings import (
    MENU_BUY, MENU_BALANCE, MENU_CONTACT, MENU_BACK, MENU_CANCEL,
    MENU_ADMIN, LANG_BTN, LANG_FLAGS, SUB_BTN,
)

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
                if not await db.has_join_request(user_id, ch["channel_id"]):
                    not_subscribed.append(ch)
        except TelegramError as e:
            if not await db.has_join_request(user_id, ch["channel_id"]):
                logger.warning(f"Kanal tekshirishda xatolik {ch['channel_id']}: {e}")
                not_subscribed.append(ch)
    return not_subscribed


def build_subscribe_keyboard(not_subscribed: list[dict], check_callback: str = "check_sub", lang: str = "uz") -> InlineKeyboardMarkup:
    """Obuna bo'lish uchun inline URL tugmalar"""
    buttons = []
    for ch in not_subscribed:
        buttons.append([
            InlineKeyboardButton(
                f"📢 {ch['channel_name']}",
                url=ch["channel_link"]
            )
        ])
    buttons.append([
        InlineKeyboardButton(SUB_BTN.get(lang, SUB_BTN["uz"]), callback_data=check_callback)
    ])
    return InlineKeyboardMarkup(buttons)


# ─── Reply Klaviaturalar (pastda turuvchi tugmalar) ───────────

def main_menu_keyboard(is_admin: bool = False, lang: str = "uz") -> ReplyKeyboardMarkup:
    """Foydalanuvchi asosiy menyusi"""
    lang_label = LANG_BTN.get(lang, LANG_BTN["uz"])
    keys = [
        [MENU_BUY.get(lang, MENU_BUY["uz"])],
        [MENU_BALANCE.get(lang, MENU_BALANCE["uz"])],
        [MENU_CONTACT.get(lang, MENU_CONTACT["uz"])],
        [lang_label],
    ]
    if is_admin:
        keys.append([MENU_ADMIN.get(lang, MENU_ADMIN["uz"])])

    return ReplyKeyboardMarkup(keys, resize_keyboard=True)


def admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Admin asosiy menyusi — O'zbekchada qoladi"""
    return ReplyKeyboardMarkup(
        [
            ["📊 Statistika", "➖ Balans ➕"],
            ["📢 Kanallar", "🌍 Davlatlar"],
            ["💳 Karta sozlash", "📨 Ommaviy xabar"],
            ["🎁 Promokodlar", "👮‍♂️ Adminlar"],
            ["💾 Zahira nusxa"],
            ["🔙 Bosh menyuga"],
        ],
        resize_keyboard=True
    )


def back_to_main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Faqat orqaga tugmasi"""
    return ReplyKeyboardMarkup(
        [[MENU_BACK.get(lang, MENU_BACK["uz"])]],
        resize_keyboard=True,
    )


def cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        [[MENU_CANCEL.get(lang, MENU_CANCEL["uz"])]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def lang_select_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash inline klaviaturasi (barcha tillarda ko'rinadi)"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        ]
    ])


def paginated_keyboard(
    items: list[tuple[str, str]],
    page: int,
    per_page: int = 14,
    prefix: str = "page",
    back_callback: str | None = None,
    lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Sahifalangan inline klaviatura"""
    total = len(items)
    start = page * per_page
    end = min(start + per_page, total)
    page_items = items[start:end]

    buttons = []
    for cb_data, label in page_items:
        buttons.append([InlineKeyboardButton(label, callback_data=cb_data)])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"page_{prefix}_{page - 1}"))
    if end < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"page_{prefix}_{page + 1}"))
    if nav:
        buttons.append(nav)

    if back_callback:
        buttons.append([InlineKeyboardButton("🔙", callback_data=back_callback)])

    return InlineKeyboardMarkup(buttons)
