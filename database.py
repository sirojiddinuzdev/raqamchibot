"""
Ma'lumotlar bazasi — SQLite (aiosqlite)
Jadvallar: users, transactions, purchases, channels, settings
"""
import aiosqlite
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_PATH = "raqamchi.db"


async def init_db():
    """Jadvallarni yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                full_name  TEXT,
                balance    REAL    DEFAULT 0.0,
                is_banned  INTEGER DEFAULT 0,
                joined_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
                referred_by INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                country    TEXT,
                country_name TEXT,
                number     TEXT,
                hash_code  TEXT,
                price      REAL,
                code       TEXT,
                password   TEXT,
                status     TEXT    DEFAULT 'pending',
                bought_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                amount      REAL,
                check_file  TEXT,
                admin_msg   TEXT,
                status      TEXT    DEFAULT 'pending',
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id  TEXT    UNIQUE,
                channel_name TEXT,
                channel_link TEXT,
                added_at    TEXT    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Default sozlamalar
        await db.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES
                ('card_number', '8600 0000 0000 0000'),
                ('card_owner', 'Bot Admin'),
                ('support_link', 'https://t.me/admin'),
                ('welcome_msg', 'Xush kelibsiz! 👋')
        """)

        # Indekslar (Tezlikni oshirish uchun)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases (user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_purchases_status ON purchases (status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_purchases_bought_at ON purchases (bought_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_deposits_user_id ON deposits (user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_deposits_status ON deposits (status)")

        await db.commit()
    logger.info("Ma'lumotlar bazasi tayyor ✅")


# ─── FOYDALANUVCHI ────────────────────────────────────────────

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def create_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users (user_id, username, full_name, referred_by)
               VALUES (?, ?, ?, ?)""",
            (user_id, username, full_name, referred_by)
        )
        await db.commit()


async def update_balance(user_id: int, delta: float):
    """Balansni delta miqdorga o'zgartiradi (+/-)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (delta, user_id)
        )
        await db.commit()


async def decrease_balance(user_id: int, amount: float) -> bool:
    """Balansdan pul yechish (agar yetarli bo'lsa), muvaffaqiyatli bo'lsa True qaytaradi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount)
        )
        await db.commit()
        return cur.rowcount > 0


async def set_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def ban_user(user_id: int, banned: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned = ? WHERE user_id = ?",
            (1 if banned else 0, user_id)
        )
        await db.commit()


async def get_all_users() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_users_page(limit: int = 10, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?", (limit, offset)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── XARID ────────────────────────────────────────────────────

async def create_purchase(
    user_id: int, country: str, country_name: str,
    number: str, hash_code: str, price: float, original_price: float = 0.0
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO purchases
               (user_id, country, country_name, number, hash_code, price, original_price)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, country, country_name, number, hash_code, price, original_price)
        )
        await db.commit()
        return cur.lastrowid


async def set_purchase_code(purchase_id: int, code: str, password: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE purchases SET code=?, password=?, status='completed' WHERE id=?",
            (code, password, purchase_id)
        )
        await db.commit()


async def get_purchase(purchase_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM purchases WHERE id = ?", (purchase_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_user_purchases(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM purchases WHERE user_id=? ORDER BY bought_at DESC LIMIT 20",
            (user_id,)
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


# ─── DEPOZIT (To'ldirish) ─────────────────────────────────────

async def create_deposit(user_id: int, check_file: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO deposits (user_id, check_file) VALUES (?, ?)",
            (user_id, check_file)
        )
        await db.commit()
        return cur.lastrowid


async def confirm_deposit(deposit_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM deposits WHERE id=?", (deposit_id,)
        ) as cur:
            row = await cur.fetchone()
        if row:
            user_id = row[0]
            await db.execute(
                """UPDATE deposits
                   SET status='confirmed', admin_msg=?, confirmed_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (str(amount), deposit_id)
            )
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()
            return user_id
        return None


async def get_deposit(deposit_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM deposits WHERE id=?", (deposit_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_pending_deposits() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM deposits WHERE status='pending' ORDER BY created_at DESC"
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


# ─── KANALLAR ─────────────────────────────────────────────────

async def get_channels() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM channels") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def add_channel(channel_id: str, channel_name: str, channel_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO channels (channel_id, channel_name, channel_link)
               VALUES (?, ?, ?)""",
            (channel_id, channel_name, channel_link)
        )
        await db.commit()


async def del_channel(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE id=?", (channel_id,))
        await db.commit()


# ─── SOZLAMALAR ───────────────────────────────────────────────

async def get_setting(key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()


async def del_setting(key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM settings WHERE key=?", (key,))
        await db.commit()


# ─── STATISTIKA ───────────────────────────────────────────────

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}

        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            stats["total_users"] = (await cur.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned=1") as cur:
            stats["banned_users"] = (await cur.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM purchases") as cur:
            stats["total_purchases"] = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM purchases WHERE status='completed'"
        ) as cur:
            stats["completed_purchases"] = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT SUM(price) FROM purchases WHERE status='completed'"
        ) as cur:
            val = (await cur.fetchone())[0]
            stats["total_revenue"] = round(val or 0, 2)

        async with db.execute(
            """SELECT country_name, COUNT(*) as cnt
               FROM purchases WHERE status='completed'
               GROUP BY country ORDER BY cnt DESC LIMIT 5"""
        ) as cur:
            rows = await cur.fetchall()
            stats["top_countries"] = rows

        async with db.execute(
            """SELECT COUNT(*) FROM users
               WHERE date(joined_at) = date('now')"""
        ) as cur:
            stats["today_users"] = (await cur.fetchone())[0]

        async with db.execute(
            """SELECT COUNT(*) FROM purchases
               WHERE date(bought_at) = date('now') AND status='completed'"""
        ) as cur:
            stats["today_purchases"] = (await cur.fetchone())[0]

        return stats
