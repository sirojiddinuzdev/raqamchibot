# Raqamchi Bot

Telegram uchun turli davlatlarning virtual raqamlarini sotib olish, balansni boshqarish va SMS kodlarni olish imkonini beruvchi bot. Bot Python va `python-telegram-bot` asosida ishlaydi, ma'lumotlarni SQLite bazasida saqlaydi hamda raqamlarni Spider Service API orqali oladi.

## Imkoniyatlar

- O'zbek, ingliz va rus tillaridagi interfeys.
- Davlatlar bo'yicha Telegram raqamlarini ko'rish va sotib olish.
- Balansni to'ldirish uchun chek yuborish va admin tasdig'i.
- Xarid qilingan raqamlar uchun SMS kodni olish.
- Xaridlar tarixi: davlat bayrog'i va nomi, sana, raqam va narx.
- Promokodlar va taklif havolalari.
- Majburiy kanal obunasini tekshirish.
- Admin panel: statistika, foydalanuvchilar, kanallar, davlatlar, to'lovlar, promokodlar va zaxira nusxalari.
- Bazaning har kuni Toshkent vaqti bilan 23:30 da adminlarga avtomatik zaxira nusxasini yuborish.

## Talablar

- Python 3.10 yoki undan yangi versiya.
- Telegram bot tokeni.
- Raqamlar uchun Spider Service API kaliti.

## O'rnatish va ishga tushirish

Loyihani yuklab olib, loyiha papkasiga kiring:

```bash
git clone <repository-url>
cd raqamchibot
```

Virtual muhit yarating va bog'liqliklarni o'rnating:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell'da virtual muhitni yoqish:

```powershell
.venv\Scripts\Activate.ps1
```

Loyiha ildizida `.env` faylini yarating:

```env
BOT_TOKEN=telegram_bot_token
ADMIN_IDS=123456789,987654321
SPIDER_API_KEY=spider_service_api_key
EXCHANGE_RATE=12000
SUPPORT_LINK=@support_username
LOG_CHANNEL=
```

So'ng botni ishga tushiring:

```bash
python bot.py
```

Ma'lumotlar bazasi birinchi ishga tushishda avtomatik yaratiladi.

## Sozlamalar

| O'zgaruvchi | Majburiy | Tavsif |
| --- | --- | --- |
| `BOT_TOKEN` | Ha | BotFather bergan Telegram bot tokeni. |
| `ADMIN_IDS` | Tavsiya qilinadi | Asosiy adminlarning Telegram ID'lari; bir nechta ID vergul bilan ajratiladi. |
| `SPIDER_API_KEY` | Ha | Spider Service API kaliti. |
| `EXCHANGE_RATE` | Yo'q | USD/so'm hisob-kitobida ishlatiladigan kurs; standart qiymati `12000`. |
| `SUPPORT_LINK` | Yo'q | Foydalanuvchilar murojaat qiladigan admin username yoki havola. |
| `LOG_CHANNEL` | Yo'q | Xarid xabarlari yuboriladigan kanal username'i yoki ID'si; bo'sh qoldirilsa xabar yuborilmaydi. |
| `RAILWAY_VOLUME_MOUNT_PATH` | Yo'q | Railway volume papkasi. Berilmasa baza loyiha katalogidagi `raqamchi.db` faylida saqlanadi. |

`ADMIN_IDS` dagi adminlar botdagi admin amallariga kirish huquqiga ega bo'ladi. Qo'shimcha adminlarni botning adminlar bo'limidan boshqarish mumkin.

## Telegram buyruqlari

- `/start` — botni boshlash va asosiy menyuni ochish.
- `/til` — interfeys tilini o'zgartirish.
- `/admin` — admin bilan bog'lanish.

Admin paneli admin foydalanuvchiga asosiy menyuda ko'rsatiladigan **Admin Panel** tugmasi orqali ochiladi.

## Ma'lumotlar va zaxira

Standart SQLite bazasi `raqamchi.db` nomi bilan yaratiladi. Deploy muhitida, jumladan Railway'da, doimiy saqlash uchun volume ulang va `RAILWAY_VOLUME_MOUNT_PATH` ni volume yo'liga sozlang. Zaxira nusxalari maxfiy foydalanuvchi va xarid ma'lumotlarini o'z ichiga oladi; ularni himoyalangan joyda saqlang.

## Xavfsizlik

- `.env` faylini, bot tokenini va API kalitlarini Git'ga qo'shmang yoki boshqalarga yubormang.
- Ishga tushirishdan oldin `.env` qiymatlarini o'zingizning bot va API ma'lumotlaringiz bilan to'ldiring.
- Admin ID'larini faqat ishonchli foydalanuvchilarga bering.
