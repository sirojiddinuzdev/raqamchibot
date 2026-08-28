# 1. Tolovni tasdiqlash va qabul qilmaslik tugmalari
- `user_deposit.py` faylida adminlarga yuboriladigan chek xabariga ikkita tugma qo'shamiz: "✅ Tasdiqlash" va "❌ Qabul qilmaslik".
- Har bir to'lov so'roviga noyob `dep_id` beramiz va bu ma'lumotni `context.bot_data` da saqlaymiz.
- Admin "Qabul qilmaslik" tugmasini bossa, undan rad etish sababini so'raymiz (bu jarayon `admin_deposits.py` va `admin_text_handler.py` da boshqariladi).
- Sabab yozilgandan so'ng (yoki "izohsiz" qoldirilsa), foydalanuvchiga to'lov qabul qilinmagani haqida xabar boradi.

# 2. Xarid xabarida raqamning oxirgi 4 xonasini yashirish
- `user_purchase.py` faylida xarid qilingan raqam `LOG_CHANNEL` ga yuborilayotganda `number[:-4] + "****"` ko'rinishida formatlanadi (Masalan: `99890123****`).

# 3. Orqaga va bekor qilish tugmalarini to'g'rilash
- Oldingi xatolik (`UnboundLocalError`) tufayli bekor qilish ishlamay qolgan edi, u to'g'rilandi. 
- Qo'shimcha ravishda `bot.py` va `helpers.py` larda barcha holatlar (state) larni tozalash (clear) mantig'ini mustahkamlaymiz.

# 4. Asl narx (_original) larni foydalanuvchidan yashirish
- `user_purchase.py` da davlatlar ro'yxati bazadan olinayotganda `WHERE key LIKE 'country_%' AND key NOT LIKE '%_original'` so'rovi orqali faqat sotuv narxi bor davlatlar ko'rsatiladi.

# 5. Tolovni tasdiqlash xatoliklari
- To'lovni tasdiqlash aslida ishlashi kerak edi, ammo "Bekor qilish"dagi xatolik ta'sir qilgan bo'lishi mumkin. To'lov tasdiqlash mantig'ini to'liq ko'zdan kechirib, muammosiz ishlashini ta'minlaymiz.

# 6. To'lov tasdiqlangach boshqa adminlardan xabarni o'chirish
- `context.bot_data` orqali har bir to'lov xabarining ID larini (barcha adminlardagi) saqlaymiz.
- Bitta admin tasdiqlashi yoki rad etishi bilan, qolgan barcha adminlardagi inline tugmalar olib tashlanadi va "✅ Admin @username tomonidan tasdiqlandi" kabi matnga o'zgartiriladi.

# 7. Kutilmagan media kelganda ogohlantirish
- `bot.py` da matn kutilayotgan holatlarda (masalan summa kiritish) agar rasm yoki video kelsa, foydalanuvchiga "Iltimos, matn yuboring" deb ogohlantiruvchi umumiy `media_fallback_handler` qo'shamiz.

## Verification Plan
1. To'lov jarayonini noldan sinab ko'rish: rasm tashlash, admin qabul qilishi/rad etishi, xabarlar o'zgarishi.
2. Davlatlar menyusini ochib `_original` yo'qligini tekshirish.
3. Raqam sotib olib, kanalga ketgan xabarda `****` borligini ko'rish.
4. Rasm yuborilishi kutilmagan joyda rasm tashlab ko'rish.
