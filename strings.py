"""
strings.py — Markaziy tarjimalar fayli
Faqat foydalanuvchiga yuboriluvchi xabarlar.
Admin panel xabarlari bu yerda yo'q.
"""

# Til belgisi
LANG_FLAGS = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}

# Til tugmasi matni (tanlangan tilga qarab)
LANG_BTN = {
    "uz": "🌐 Til",
    "en": "🌐 Language",
    "ru": "🌐 Язык",
}

# Asosiy menyu tugmalar
MENU_BUY = {
    "uz": "📱 Raqam sotib olish",
    "en": "📱 Buy Number",
    "ru": "📱 Купить номер",
}
BUY_TOP_CHEAP_BTN = {
    "uz": "🔝 Eng arzon davlatlar",
    "en": "🔝 Cheapest countries",
    "ru": "🔝 Самые дешёвые страны",
}
MENU_DEPOSIT = {
    "uz": "💳 Hisobni to'ldirish",
    "en": "💳 Top up balance",
    "ru": "💳 Пополнить баланс",
}
MENU_BALANCE = {
    "uz": "💰 Hisobim",
    "en": "💰 My balance",
    "ru": "💰 Мой баланс",
}
MENU_HISTORY = {
    "uz": "📜 Tarix",
    "en": "📜 History",
    "ru": "📜 История",
}
MENU_CONTACT = {
    "uz": "📞 Admin bilan bog'lanish",
    "en": "📞 Contact admin",
    "ru": "📞 Связаться с админом",
}
MENU_PROMO = {
    "uz": "🎁 Promokod",
    "en": "🎁 Promo code",
    "ru": "🎁 Промокод",
}
ACCOUNT_DEPOSIT_BTN = {
    "uz": "💳 Hisobni to'ldirish",
    "en": "💳 Top up balance",
    "ru": "💳 Пополнить баланс",
}
ACCOUNT_PROMO_BTN = {
    "uz": "🎁 Promokod kiritish",
    "en": "🎁 Enter promo code",
    "ru": "🎁 Ввести промокод",
}
MENU_BACK = {
    "uz": "🔙 Bosh menyuga",
    "en": "🔙 Back to menu",
    "ru": "🔙 В главное меню",
}
MENU_CANCEL = {
    "uz": "❌ Bekor qilish",
    "en": "❌ Cancel",
    "ru": "❌ Отмена",
}
MENU_ADMIN = {
    "uz": "👨‍💻 Admin Panel",
    "en": "👨‍💻 Admin Panel",
    "ru": "👨‍💻 Admin Panel",
}

# ----- START / TIL TANLASH -----

CHOOSE_LANGUAGE = {
    "uz": "Quyidagi tillardan birini tanlang:",
    "en": "Please choose one of the following languages:",
    "ru": "Выберите один из следующих языков:",
}

LANG_CHANGED = {
    "uz": "✅ Til o'zgartirildi: O'zbekcha",
    "en": "✅ Language changed: English",
    "ru": "✅ Язык изменён: Русский",
}

# ----- WELCOME / START -----

WELCOME = {
    "uz": "👋 Assalomu alaykum, {name}!\n\n"
          "🤖 Raqamchi Bot — Telegram uchun turli davlatlarning anonim va virtual akkauntlarini "
          "tezkor hamda xavfsiz sotib olish xizmati.\n"
          "Menyudan tilni almashtirishingiz mumkin 🇺🇿🇺🇸🇷🇺:",
    "en": "👋 <b>Welcome, {name}!</b>\n\n"
          "🤖 <b>Raqamchi Bot</b> — Telegram account number purchase service\n\n"
          "💰 <b>Balance:</b> {balance} UZS\n"
          "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
          "👇 Use the menu below:",
    "ru": "👋 <b>Добро пожаловать, {name}!</b>\n\n"
          "🤖 <b>Raqamchi Bot</b> — Сервис покупки номеров Telegram аккаунтов\n\n"
          "💰 <b>Баланс:</b> {balance} сум\n"
          "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
          "👇 Используйте меню ниже:",
}

SUB_REQUIRED = {
    "uz": "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n",
    "en": "⚠️ <b>Please subscribe to the following channels to use the bot:</b>\n\n",
    "ru": "⚠️ <b>Для использования бота подпишитесь на следующие каналы:</b>\n\n",
}

SUB_BTN = {
    "uz": "✅ Obuna bo'ldim",
    "en": "✅ I subscribed",
    "ru": "✅ Я подписался",
}

SUB_NOT_YET = {
    "uz": "Siz hali obuna bo'lmagansiz",
    "en": "You haven't subscribed yet",
    "ru": "Вы ещё не подписались",
}

SUB_FAIL = {
    "uz": "❌ Siz hali barcha kanallarga obuna bo'lmadingiz yoki so'rov yubormadingiz!\n\n",
    "en": "❌ You haven't subscribed to all channels yet!\n\n",
    "ru": "❌ Вы ещё не подписались на все каналы!\n\n",
}

SUB_CONFIRMED = {
    "uz": "✅ <b>Obuna tasdiqlandi!</b>\n\n"
          "👋 Xush kelibsiz, <b>{name}</b>!\n\n"
          "💰 <b>Hisobingiz:</b> {balance} so'm\n"
          "🆔 <b>ID:</b> <code>{user_id}</code>",
    "en": "✅ <b>Subscription confirmed!</b>\n\n"
          "👋 Welcome, <b>{name}</b>!\n\n"
          "💰 <b>Balance:</b> {balance} UZS\n"
          "🆔 <b>ID:</b> <code>{user_id}</code>",
    "ru": "✅ <b>Подписка подтверждена!</b>\n\n"
          "👋 Добро пожаловать, <b>{name}</b>!\n\n"
          "💰 <b>Баланс:</b> {balance} сум\n"
          "🆔 <b>ID:</b> <code>{user_id}</code>",
}

BANNED = {
    "uz": "🚫 Siz botdan bloklangansiz.",
    "en": "🚫 You are banned from this bot.",
    "ru": "🚫 Вы заблокированы в этом боте.",
}

MAIN_MENU_TEXT = {
    "uz": "🏠 <b>Bosh menyu</b>\n\n💰 <b>Hisobingiz:</b> {balance} so'm\n🆔 <b>ID:</b> <code>{user_id}</code>",
    "en": "🏠 <b>Main menu</b>\n\n💰 <b>Balance:</b> {balance} UZS\n🆔 <b>ID:</b> <code>{user_id}</code>",
    "ru": "🏠 <b>Главное меню</b>\n\n💰 <b>Баланс:</b> {balance} сум\n🆔 <b>ID:</b> <code>{user_id}</code>",
}

START_TOPUP_BTN = {
    "uz": "💳 Balansni to'ldirish",
    "en": "💳 Top up balance",
    "ru": "💳 Пополнить баланс",
}

MAIN_MENU_PROMPT = {
    "uz": "👇 Kerakli bo'limni tanlang:",
    "en": "👇 Choose an option from the menu:",
    "ru": "👇 Выберите нужный раздел в меню:",
}

# ----- BALANCE -----

BALANCE_TEXT = {
    "uz": "💰 <b>Hisob ma'lumotlari</b>\n\n"
          "👤 Ism: {name}\n"
          "🆔 ID: <code>{user_id}</code>\n"
          "💵 Balans: <b>{balance} so'm</b>\n"
          "📅 Qo'shilgan: {joined}",
    "en": "💰 <b>Account info</b>\n\n"
          "👤 Name: {name}\n"
          "🆔 ID: <code>{user_id}</code>\n"
          "💵 Balance: <b>{balance} UZS</b>\n"
          "📅 Joined: {joined}",
    "ru": "💰 <b>Информация об аккаунте</b>\n\n"
          "👤 Имя: {name}\n"
          "🆔 ID: <code>{user_id}</code>\n"
          "💵 Баланс: <b>{balance} сум</b>\n"
          "📅 Дата регистрации: {joined}",
}

HISTORY_HEADER = {
    "uz": "📜 <b>Raqamlar xaridi tarixi:</b>\n\n",
    "en": "📜 <b>Number purchase history:</b>\n\n",
    "ru": "📜 <b>История покупки номеров:</b>\n\n",
}
HISTORY_EMPTY = {
    "uz": "📭 Hozircha xaridlar tarixi bo'sh.\n\nHisobingizni to'ldirib, raqam sotib olishingiz mumkin.",
    "en": "📭 Your purchase history is empty for now.\n\nTop up your balance to buy a number.",
    "ru": "📭 История покупок пока пуста.\n\nПополните баланс, чтобы купить номер.",
}

USER_NOT_FOUND = {
    "uz": "❌ Foydalanuvchi topilmadi.",
    "en": "❌ User not found.",
    "ru": "❌ Пользователь не найден.",
}

# ----- CONTACT ADMIN -----

CONTACT_ADMIN_TEXT = {
    "uz": "📞 <b>Admin bilan bog'lanish</b>\n\nHar qanday savol yoki muammo uchun:\n👉 {link}",
    "en": "📞 <b>Contact admin</b>\n\nFor any questions or issues:\n👉 {link}",
    "ru": "📞 <b>Связаться с админом</b>\n\nПо любым вопросам или проблемам:\n👉 {link}",
}

# ----- DEPOSIT -----

DEPOSIT_ENTER_AMOUNT = {
    "uz": "💰 <b>Qancha summa o'tkazmoqchisiz?</b>\n\nIltimos, summani raqamlarda kiriting (masalan: 50000):",
    "en": "💰 <b>How much do you want to deposit?</b>\n\nPlease enter the amount in numbers (e.g. 50000):",
    "ru": "💰 <b>Сколько хотите пополнить?</b>\n\nПожалуйста, введите сумму цифрами (например: 50000):",
}

DEPOSIT_NO_CARD = {
    "uz": "❌ Hozircha hisobni to'ldirish imkonsiz. Adminga murojaat qiling.",
    "en": "❌ Deposits are currently unavailable. Please contact admin.",
    "ru": "❌ Пополнение баланса временно недоступно. Обратитесь к администратору.",
}

DEPOSIT_DETAILS = {
    "uz": "💳 <b>Hisobni to'ldirish</b>\n\n"
          "Kiritilgan summa: <b>{amount} so'm</b>\n\n"
          "Karta raqami: <code>{card}</code>\n"
          "Qabul qiluvchi: <b>{owner}</b>\n\n"
          "👇 Ushbu kartaga <b>{amount} so'm</b> o'tkazgach, to'lov <b>cheki (skrinshotini)</b> shu yerga yuboring.\n"
          "⚠️ <i>Sizda to'lovni tasdiqlash uchun 5 daqiqa vaqt bor.</i>",
    "en": "💳 <b>Top up balance</b>\n\n"
          "Amount: <b>{amount} UZS</b>\n\n"
          "Card number: <code>{card}</code>\n"
          "Cardholder: <b>{owner}</b>\n\n"
          "👇 After transferring <b>{amount} UZS</b> to this card, send the payment <b>receipt (screenshot)</b> here.\n"
          "⚠️ <i>You have 5 minutes to confirm the payment.</i>",
    "ru": "💳 <b>Пополнение баланса</b>\n\n"
          "Сумма: <b>{amount} сум</b>\n\n"
          "Номер карты: <code>{card}</code>\n"
          "Получатель: <b>{owner}</b>\n\n"
          "👇 После перевода <b>{amount} сум</b> на эту карту, отправьте <b>чек (скриншот)</b> сюда.\n"
          "⚠️ <i>У вас 5 минут для подтверждения платежа.</i>",
}

DEPOSIT_SENT = {
    "uz": "✅ To'lov chekingiz adminga yuborildi. Tez orada hisobingiz to'ldiriladi.",
    "en": "✅ Your payment receipt has been sent to the admin. Your balance will be topped up shortly.",
    "ru": "✅ Ваш чек отправлен администратору. Баланс будет пополнен в ближайшее время.",
}

DEPOSIT_CANCELLED = {
    "uz": "❌ Hisobni to'ldirish bekor qilindi.",
    "en": "❌ Deposit cancelled.",
    "ru": "❌ Пополнение баланса отменено.",
}

DEPOSIT_TIMEOUT = {
    "uz": "⏳ To'lov qilish uchun berilgan 5 daqiqa vaqt tugadi. Qaytadan 'Hisobni to'ldirish' tugmasi orqali urinib ko'ring.",
    "en": "⏳ The 5-minute payment window has expired. Please try again via 'Top up balance'.",
    "ru": "⏳ Время на оплату (5 минут) истекло. Попробуйте снова через кнопку 'Пополнить баланс'.",
}

DEPOSIT_INVALID = {
    "uz": "❌ Iltimos, to'lov chekini (rasm/skrinshot yoki fayl) yuboring yoki '❌ Bekor qilish' tugmasini bosing.",
    "en": "❌ Please send a payment receipt (image/screenshot or file) or press '❌ Cancel'.",
    "ru": "❌ Пожалуйста, отправьте чек об оплате (изображение/скриншот или файл) или нажмите '❌ Отмена'.",
}

# ----- PURCHASE -----

LOADING_COUNTRIES = {
    "uz": "⏳ Mavjud davlatlar yuklanmoqda...",
    "en": "⏳ Loading available countries...",
    "ru": "⏳ Загрузка доступных стран...",
}

NO_COUNTRIES = {
    "uz": "❌ Hozircha sotuvda davlatlar yo'q.\nKeyinroq urinib ko'ring.",
    "en": "❌ No countries available at the moment.\nPlease try again later.",
    "ru": "❌ В данный момент нет доступных стран.\nПопробуйте позже.",
}

SELECT_COUNTRY = {
    "uz": "🌍 <b>Davlat tanlang</b>\n\nQuyidagi davlatlardan birini tanlang:",
    "en": "🌍 <b>Select country</b>\n\nChoose one of the following countries:",
    "ru": "🌍 <b>Выберите страну</b>\n\nВыберите одну из следующих стран:",
}

TOP10_TITLE = {
    "uz": "🔝 <b>Eng arzon 10 ta davlat</b>\n\nQuyidagilardan birini tanlang:",
    "en": "🔝 <b>Top 10 cheapest countries</b>\n\nChoose one of the following:",
    "ru": "🔝 <b>Топ 10 дешёвых стран</b>\n\nВыберите одну из следующих:",
}

TOP10_ALL_BTN = {
    "uz": "🔙 Barcha davlatlar",
    "en": "🔙 All countries",
    "ru": "🔙 Все страны",
}

COUNTRY_UNAVAILABLE = {
    "uz": "❌ Bu davlat hozir mavjud emas.",
    "en": "❌ This country is currently unavailable.",
    "ru": "❌ Эта страна сейчас недоступна.",
}

CONFIRM_BUY = {
    "uz": "🌍 <b>Tanlangan davlat:</b> {country}\n"
          "💵 <b>Narxi:</b> {price} so'm\n"
          "💰 <b>Balansingiz:</b> {balance} so'm\n\n"
          "✅ Balansingiz yetarli. Xaridni tasdiqlaysizmi?",
    "en": "🌍 <b>Selected country:</b> {country}\n"
          "💵 <b>Price:</b> {price} UZS\n"
          "💰 <b>Balance:</b> {balance} UZS\n\n"
          "✅ Balance sufficient. Confirm purchase?",
    "ru": "🌍 <b>Выбранная страна:</b> {country}\n"
          "💵 <b>Цена:</b> {price} сум\n"
          "💰 <b>Ваш баланс:</b> {balance} сум\n\n"
          "✅ Баланса достаточно. Подтвердить покупку?",
}

INSUFFICIENT_BALANCE = {
    "uz": "🌍 <b>Tanlangan davlat:</b> {country}\n"
          "💵 <b>Narxi:</b> {price} so'm\n"
          "💰 <b>Balansingiz:</b> {balance} so'm\n\n"
          "❌ <b>Balansingiz yetarli emas!</b>\n"
          "Kerakli: {price} so'm | Yetishmaydi: {diff} so'm\n\n"
          "💳 Hisobni to'ldiring!",
    "en": "🌍 <b>Selected country:</b> {country}\n"
          "💵 <b>Price:</b> {price} UZS\n"
          "💰 <b>Balance:</b> {balance} UZS\n\n"
          "❌ <b>Insufficient balance!</b>\n"
          "Required: {price} UZS | Missing: {diff} UZS\n\n"
          "💳 Please top up your balance!",
    "ru": "🌍 <b>Выбранная страна:</b> {country}\n"
          "💵 <b>Цена:</b> {price} сум\n"
          "💰 <b>Ваш баланс:</b> {balance} сум\n\n"
          "❌ <b>Недостаточно средств!</b>\n"
          "Нужно: {price} сум | Не хватает: {diff} сум\n\n"
          "💳 Пополните баланс!",
}

BUY_CONFIRM_BTN = {
    "uz": "✅ Ha, sotib olaman",
    "en": "✅ Yes, buy",
    "ru": "✅ Да, купить",
}

BUY_CANCEL_BTN = {
    "uz": "❌ Bekor qilish",
    "en": "❌ Cancel",
    "ru": "❌ Отмена",
}

BUY_CANCELLED = {
    "uz": "❌ Bekor qilindi.",
    "en": "❌ Cancelled.",
    "ru": "❌ Отменено.",
}

BUYING_LOADING = {
    "uz": "⏳ Raqam sotib olinmoqda, iltimos kuting...",
    "en": "⏳ Purchasing number, please wait...",
    "ru": "⏳ Покупаем номер, пожалуйста подождите...",
}

NO_NUMBER_FOUND = {
    "uz": "❌ <b>Bu davlat uchun raqam topilmadi!</b>\nBoshqa davlatni tanlang yoki keyinroq urinib ko'ring.\n(Pulingiz hisobingizga qaytarildi)",
    "en": "❌ <b>No number found for this country!</b>\nChoose another country or try later.\n(Your money has been refunded)",
    "ru": "❌ <b>Номер для этой страны не найден!</b>\nВыберите другую страну или попробуйте позже.\n(Деньги возвращены на баланс)",
}

BUY_SUCCESS = {
    "uz": "✅ <b>Raqam muvaffaqiyatli sotib olindi!</b>\n\n"
          "🌍 Davlat: {country}\n"
          "📱 Raqam: <code>{number}</code>\n"
          "💵 Narxi: {price} so'm\n"
          "💰 Qolgan balans: {balance} so'm\n\n"
          "⚠️ <b>DIQQAT:</b> Raqamni rasmiy Telegram ilovasida UMUMAN ishlatmang! Aks holda darhol bloklanadi.\n"
          "👉 Faqat norasmiy ilovalardan (Telegram X, Plus Messenger, Nicegram va h.k.) foydalaning.\n\n"
          "📨 SMS kodni olish uchun tugmani bosing.",
    "en": "✅ <b>Number purchased successfully!</b>\n\n"
          "🌍 Country: {country}\n"
          "📱 Number: <code>{number}</code>\n"
          "💵 Price: {price} UZS\n"
          "💰 Remaining balance: {balance} UZS\n\n"
          "⚠️ <b>WARNING:</b> NEVER use this number in the official Telegram app! It will be immediately blocked.\n"
          "👉 Only use unofficial apps (Telegram X, Plus Messenger, Nicegram, etc.)\n\n"
          "📨 Press the button to receive the SMS code.",
    "ru": "✅ <b>Номер успешно куплен!</b>\n\n"
          "🌍 Страна: {country}\n"
          "📱 Номер: <code>{number}</code>\n"
          "💵 Цена: {price} сум\n"
          "💰 Остаток на балансе: {balance} сум\n\n"
          "⚠️ <b>ВНИМАНИЕ:</b> НИКОГДА не используйте этот номер в официальном Telegram! Он будет немедленно заблокирован.\n"
          "👉 Используйте только неофициальные приложения (Telegram X, Plus Messenger, Nicegram и др.)\n\n"
          "📨 Нажмите кнопку для получения SMS-кода.",
}

GET_CODE_BTN = {
    "uz": "📨 SMS Kodni olish",
    "en": "📨 Get SMS Code",
    "ru": "📨 Получить SMS код",
}

RETRY_BTN = {
    "uz": "🔄 Qayta tekshirish",
    "en": "🔄 Check again",
    "ru": "🔄 Проверить снова",
}

CODE_WAITING = {
    "uz": "🌍 Davlat: {country}\n📱 Raqam: <code>{number}</code>\n\n⏳ <b>SMS kod hali kelmadi.</b> ({time})\nBiroz kuting va qayta tekshiring (1–3 daqiqa).",
    "en": "🌍 Country: {country}\n📱 Number: <code>{number}</code>\n\n⏳ <b>SMS code not yet received.</b> ({time})\nWait a moment and check again (1–3 minutes).",
    "ru": "🌍 Страна: {country}\n📱 Номер: <code>{number}</code>\n\n⏳ <b>SMS код ещё не получен.</b> ({time})\nПодождите немного и проверьте снова (1–3 минуты).",
}

CODE_ALREADY = {
    "uz": "✅ <b>SMS Kod:</b>\n\n🌍 Davlat: {country}\n📱 Raqam: <code>{number}</code>\n💬 <b>Kod: <code>{code}</code></b>\n🔑 Parol: <code>{password}</code>",
    "en": "✅ <b>SMS Code:</b>\n\n🌍 Country: {country}\n📱 Number: <code>{number}</code>\n💬 <b>Code: <code>{code}</code></b>\n🔑 Password: <code>{password}</code>",
    "ru": "✅ <b>SMS Код:</b>\n\n🌍 Страна: {country}\n📱 Номер: <code>{number}</code>\n💬 <b>Код: <code>{code}</code></b>\n🔑 Пароль: <code>{password}</code>",
}

CODE_ARRIVED = {
    "uz": "✅ <b>SMS Kod keldi!</b>\n\n"
          "🌍 Davlat: {country}\n"
          "📱 Raqam: <code>{number}</code>\n"
          "💵 Narxi: {price} so'm\n"
          "💬 <b>Kod: <code>{code}</code></b>\n"
          "🔑 Parol: <code>{password}</code>\n\n"
          "⚠️ <b>DIQQAT:</b> Raqamni rasmiy Telegram ilovasida UMUMAN faollashtirmang (bloklanadi)!\n"
          "👉 Faqat norasmiy ilovalardan (Telegram X, Plus Messenger, Nicegram) foydalaning.",
    "en": "✅ <b>SMS Code received!</b>\n\n"
          "🌍 Country: {country}\n"
          "📱 Number: <code>{number}</code>\n"
          "💵 Price: {price} UZS\n"
          "💬 <b>Code: <code>{code}</code></b>\n"
          "🔑 Password: <code>{password}</code>\n\n"
          "⚠️ <b>WARNING:</b> NEVER activate this number in the official Telegram app (it will be blocked)!\n"
          "👉 Only use unofficial apps (Telegram X, Plus Messenger, Nicegram).",
    "ru": "✅ <b>SMS Код получен!</b>\n\n"
          "🌍 Страна: {country}\n"
          "📱 Номер: <code>{number}</code>\n"
          "💵 Цена: {price} сум\n"
          "💬 <b>Код: <code>{code}</code></b>\n"
          "🔑 Пароль: <code>{password}</code>\n\n"
          "⚠️ <b>ВНИМАНИЕ:</b> НИКОГДА не активируйте этот номер в официальном Telegram (заблокируют)!\n"
          "👉 Используйте только неофициальные приложения (Telegram X, Plus Messenger, Nicegram).",
}

PURCHASE_NOT_FOUND = {
    "uz": "❌ Xarid topilmadi.",
    "en": "❌ Purchase not found.",
    "ru": "❌ Покупка не найдена.",
}

PURCHASE_ERROR = {
    "uz": "❌ Xatolik. Qaytadan urinib ko'ring.",
    "en": "❌ An error occurred. Please try again.",
    "ru": "❌ Произошла ошибка. Попробуйте снова.",
}

BALANCE_INSUFFICIENT_ALERT = {
    "uz": "❌ Balansingiz yetarli emas!",
    "en": "❌ Insufficient balance!",
    "ru": "❌ Недостаточно средств!",
}

# ----- PROMO -----

PROMO_ENTER = {
    "uz": "🎁 Promokodingizni kiriting:",
    "en": "🎁 Enter your promo code:",
    "ru": "🎁 Введите ваш промокод:",
}
