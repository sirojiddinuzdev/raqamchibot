import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
EXCHANGE_RATE = int(os.getenv("EXCHANGE_RATE", "12000"))
DB_PATH = "raqamchi.db"

def migrate():
    print(f"Baza migratsiyasi boshlandi... Valyuta kursi: {EXCHANGE_RATE}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. users jadvali (balance)
    cursor.execute("UPDATE users SET balance = balance * ?", (EXCHANGE_RATE,))
    print(f"Users jadvali yangilandi: {cursor.rowcount} ta qator")

    # 2. settings jadvali (country narxlari)
    cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'country_%'")
    rows = cursor.fetchall()
    count = 0
    for key, value in rows:
        try:
            old_price = float(value)
            new_price = int(old_price * EXCHANGE_RATE) # Butun son qilib saqlaymiz (so'm)
            cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (str(new_price), key))
            count += 1
        except Exception as e:
            print(f"Error {key}: {e}")
    print(f"Settings jadvali yangilandi: {count} ta davlat narxi")

    # 3. purchases jadvali (price)
    cursor.execute("UPDATE purchases SET price = price * ?", (EXCHANGE_RATE,))
    print(f"Purchases jadvali yangilandi: {cursor.rowcount} ta qator")

    # 4. deposits jadvali (amount)
    cursor.execute("UPDATE deposits SET amount = amount * ?", (EXCHANGE_RATE,))
    print(f"Deposits jadvali yangilandi: {cursor.rowcount} ta qator")

    conn.commit()
    conn.close()
    print("Migratsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    migrate()
