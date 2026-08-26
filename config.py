# =============================================
# RAQAMCHI BOT — Konfiguratsiya fayli
# =============================================

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin ID lari (bir nechta admin bo'lishi mumkin)
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Spider-service API kaliti
SPIDER_API_KEY = os.getenv("SPIDER_API_KEY", "")

# Karta raqami (to'ldirish uchun)
CARD_NUMBER = "8600 0000 0000 0000"
CARD_OWNER = "Bot Admin"

# Admin bilan bog'lanish linki
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "@Sirojiddin_Ibn_Baxtiyor")

# Xaridlar haqida xabar boradigan kanal ID si yoki username si (masalan: "@log_kanalim")
# Agar xabar borishini xohlamasangiz bo'sh qoldiring: ""
LOG_CHANNEL = os.getenv("LOG_CHANNEL", "")
