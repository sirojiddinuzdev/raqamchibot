"""PostgreSQL database access for the bot."""

import json
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")
_pool: AsyncConnectionPool | None = None

BACKUP_TABLES = (
    "users",
    "purchases",
    "deposits",
    "channels",
    "promocodes",
    "promocode_uses",
    "join_requests",
    "settings",
)

_BACKUP_ORDER_BY = {
    "users": "user_id",
    "purchases": "id",
    "deposits": "id",
    "channels": "id",
    "promocodes": "id",
    "promocode_uses": "user_id, promocode_id",
    "join_requests": "user_id, chat_id",
    "settings": "key",
}

_SEQUENCE_TABLES = ("purchases", "deposits", "channels", "promocodes")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[AsyncConnection[Any], None]:
    """Acquire a pooled PostgreSQL connection for one transaction."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized; call init_db() first.")

    async with _pool.connection() as connection:
        yield connection


async def _initialize_database() -> None:
    """Open the PostgreSQL pool and apply the idempotent initial schema."""
    global _pool

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is required. Configure a PostgreSQL connection URL."
        )

    if _pool is None:
        _pool = AsyncConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            open=False,
        )
        try:
            await _pool.open(wait=True)
        except Exception:
            await _pool.close()
            _pool = None
            raise

    async with get_connection() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version    INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP::text)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                balance     DOUBLE PRECISION DEFAULT 0.0,
                is_banned   INTEGER DEFAULT 0,
                joined_at   TEXT DEFAULT (
                    to_char(CURRENT_TIMESTAMP AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
                ),
                referred_by BIGINT,
                lang        TEXT DEFAULT 'uz'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id             BIGSERIAL PRIMARY KEY,
                user_id        BIGINT,
                country        TEXT,
                country_name   TEXT,
                number         TEXT,
                hash_code      TEXT,
                price          DOUBLE PRECISION,
                code           TEXT,
                password       TEXT,
                status         TEXT DEFAULT 'pending',
                bought_at      TEXT DEFAULT (
                    to_char(CURRENT_TIMESTAMP AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
                ),
                original_price DOUBLE PRECISION DEFAULT 0.0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id           BIGSERIAL PRIMARY KEY,
                user_id      BIGINT,
                amount       DOUBLE PRECISION,
                check_file   TEXT,
                admin_msg    TEXT,
                status       TEXT DEFAULT 'pending',
                created_at   TEXT DEFAULT (
                    to_char(CURRENT_TIMESTAMP AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
                ),
                confirmed_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id           BIGSERIAL PRIMARY KEY,
                channel_id   TEXT UNIQUE,
                channel_name TEXT,
                channel_link TEXT,
                added_at     TEXT DEFAULT (
                    to_char(CURRENT_TIMESTAMP AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
                )
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promocodes (
                id         BIGSERIAL PRIMARY KEY,
                code       TEXT UNIQUE,
                amount     DOUBLE PRECISION,
                uses       INTEGER DEFAULT 0,
                max_uses   INTEGER DEFAULT 1,
                expires_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promocode_uses (
                user_id      BIGINT,
                promocode_id BIGINT,
                UNIQUE(user_id, promocode_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS join_requests (
                user_id BIGINT,
                chat_id TEXT,
                UNIQUE(user_id, chat_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Keep databases created by earlier PostgreSQL schema versions upgradeable.
        await db.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'uz'"
        )
        await db.execute(
            "ALTER TABLE purchases ADD COLUMN IF NOT EXISTS "
            "original_price DOUBLE PRECISION DEFAULT 0.0"
        )

        await db.execute("""
            INSERT INTO settings (key, value) VALUES
                ('card_number', '8600 0000 0000 0000'),
                ('card_owner', 'Bot Admin'),
                ('support_link', 'https://t.me/admin'),
                ('welcome_msg', 'Xush kelibsiz! 👋')
            ON CONFLICT (key) DO NOTHING
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases (user_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_status ON purchases (status)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_bought_at ON purchases (bought_at)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_deposits_user_id ON deposits (user_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_deposits_status ON deposits (status)"
        )
        await db.execute(
            "INSERT INTO schema_migrations (version) VALUES (1) "
            "ON CONFLICT (version) DO NOTHING"
        )

    logger.info("PostgreSQL database is ready")


async def init_db() -> None:
    try:
        await _initialize_database()
    except Exception:
        await close_db()
        raise


async def close_db() -> None:
    """Close the PostgreSQL pool during application shutdown."""
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_user(user_id: int) -> dict | None:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = await cur.fetchone()
            return dict(row) if row else None


async def create_user(
    user_id: int, username: str, full_name: str, referred_by: int | None = None
) -> None:
    async with get_connection() as db:
        await db.execute(
            """INSERT INTO users (user_id, username, full_name, referred_by)
               VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING""",
            (user_id, username, full_name, referred_by),
        )


async def get_user_lang(user_id: int) -> str:
    async with get_connection() as db:
        row = await (await db.execute(
            "SELECT lang FROM users WHERE user_id = %s", (user_id,)
        )).fetchone()
        return row[0] if row and row[0] else "uz"


async def set_user_lang(user_id: int, lang: str) -> None:
    async with get_connection() as db:
        await db.execute(
            "UPDATE users SET lang = %s WHERE user_id = %s", (lang, user_id)
        )


async def update_balance(user_id: int, delta: float) -> None:
    async with get_connection() as db:
        await db.execute(
            "UPDATE users SET balance = balance + %s WHERE user_id = %s",
            (delta, user_id),
        )


async def decrease_balance(user_id: int, amount: float) -> bool:
    async with get_connection() as db:
        cur = await db.execute(
            "UPDATE users SET balance = balance - %s "
            "WHERE user_id = %s AND balance >= %s",
            (amount, user_id, amount),
        )
        return cur.rowcount > 0


async def set_balance(user_id: int, amount: float) -> None:
    async with get_connection() as db:
        await db.execute(
            "UPDATE users SET balance = %s WHERE user_id = %s", (amount, user_id)
        )


async def get_all_users() -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM users")
            return [dict(row) for row in await cur.fetchall()]


async def get_users_page(limit: int = 10, offset: int = 0) -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM users ORDER BY joined_at DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return [dict(row) for row in await cur.fetchall()]


async def get_users_count() -> int:
    async with get_connection() as db:
        row = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        return row[0] if row else 0


async def get_settings() -> dict:
    async with get_connection() as db:
        rows = await (await db.execute("SELECT key, value FROM settings")).fetchall()
        return {key: value for key, value in rows}


async def add_join_request(user_id: int, chat_id: str) -> None:
    async with get_connection() as db:
        await db.execute(
            "INSERT INTO join_requests (user_id, chat_id) VALUES (%s, %s) "
            "ON CONFLICT (user_id, chat_id) DO NOTHING",
            (user_id, str(chat_id)),
        )


async def has_join_request(user_id: int, chat_id: str) -> bool:
    chat_str = str(chat_id)
    variations = [chat_str]
    if not chat_str.startswith("-100"):
        if chat_str.startswith("-"):
            variations.append(f"-100{chat_str[1:]}")
        else:
            variations.append(f"-100{chat_str}")

    async with get_connection() as db:
        for channel_id in variations:
            row = await (await db.execute(
                "SELECT 1 FROM join_requests WHERE user_id = %s AND chat_id = %s",
                (user_id, channel_id),
            )).fetchone()
            if row is not None:
                return True
        return False


async def create_purchase(
    user_id: int,
    country: str,
    country_name: str,
    number: str,
    hash_code: str,
    price: float,
    original_price: float = 0.0,
) -> int:
    async with get_connection() as db:
        row = await (await db.execute(
            """INSERT INTO purchases
               (user_id, country, country_name, number, hash_code, price, original_price)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (user_id, country, country_name, number, hash_code, price, original_price),
        )).fetchone()
        return row[0]


async def set_purchase_code(purchase_id: int, code: str, password: str) -> None:
    async with get_connection() as db:
        await db.execute(
            "UPDATE purchases SET code = %s, password = %s, status = 'completed' "
            "WHERE id = %s",
            (code, password, purchase_id),
        )


async def get_purchase(purchase_id: int) -> dict | None:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM purchases WHERE id = %s", (purchase_id,))
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_user_purchases(user_id: int) -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM purchases WHERE user_id = %s "
                "ORDER BY bought_at DESC LIMIT 20",
                (user_id,),
            )
            return [dict(row) for row in await cur.fetchall()]


async def get_user_purchase_history(
    user_id: int, offset: int = 0, limit: int = 11
) -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM purchases WHERE user_id = %s AND status = 'completed' "
                "ORDER BY bought_at DESC, id DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset),
            )
            return [dict(row) for row in await cur.fetchall()]


async def create_deposit(user_id: int, check_file: str) -> int:
    async with get_connection() as db:
        row = await (await db.execute(
            "INSERT INTO deposits (user_id, check_file) VALUES (%s, %s) RETURNING id",
            (user_id, check_file),
        )).fetchone()
        return row[0]


async def get_channels() -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM channels")
            return [dict(row) for row in await cur.fetchall()]


async def add_channel(channel_id: str, channel_name: str, channel_link: str) -> None:
    async with get_connection() as db:
        await db.execute(
            """INSERT INTO channels (channel_id, channel_name, channel_link)
               VALUES (%s, %s, %s)
               ON CONFLICT (channel_id) DO UPDATE SET
                   channel_name = EXCLUDED.channel_name,
                   channel_link = EXCLUDED.channel_link""",
            (channel_id, channel_name, channel_link),
        )


async def del_channel(channel_id: int) -> None:
    async with get_connection() as db:
        await db.execute("DELETE FROM channels WHERE id = %s", (channel_id,))


async def get_setting(key: str) -> str | None:
    async with get_connection() as db:
        row = await (await db.execute(
            "SELECT value FROM settings WHERE key = %s", (key,)
        )).fetchone()
        return row[0] if row else None


async def set_setting(key: str, value: str) -> None:
    async with get_connection() as db:
        await db.execute(
            """INSERT INTO settings (key, value) VALUES (%s, %s)
               ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value""",
            (key, value),
        )


async def del_setting(key: str) -> None:
    async with get_connection() as db:
        await db.execute("DELETE FROM settings WHERE key = %s", (key,))


async def get_stats() -> dict:
    async with get_connection() as db:
        stats = {}
        queries = {
            "total_users": "SELECT COUNT(*) FROM users",
            "banned_users": "SELECT COUNT(*) FROM users WHERE is_banned = 1",
            "total_purchases": "SELECT COUNT(*) FROM purchases",
            "completed_purchases": (
                "SELECT COUNT(*) FROM purchases WHERE status = 'completed'"
            ),
            "total_revenue": (
                "SELECT SUM(price) FROM purchases WHERE status = 'completed'"
            ),
            "today_users": (
                "SELECT COUNT(*) FROM users "
                "WHERE joined_at::date = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date"
            ),
            "today_purchases": (
                "SELECT COUNT(*) FROM purchases "
                "WHERE bought_at::date = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date "
                "AND status = 'completed'"
            ),
        }
        for key, query in queries.items():
            row = await (await db.execute(query)).fetchone()
            stats[key] = row[0] if row else 0

        stats["total_revenue"] = round(stats["total_revenue"] or 0, 2)
        stats["top_countries"] = await (await db.execute(
            """SELECT country_name, COUNT(*) AS cnt
               FROM purchases
               WHERE status = 'completed'
               GROUP BY country, country_name
               ORDER BY cnt DESC LIMIT 5"""
        )).fetchall()
        return stats


async def create_promocode(code: str, amount: float, max_uses: int) -> None:
    async with get_connection() as db:
        await db.execute(
            "INSERT INTO promocodes (code, amount, max_uses) VALUES (%s, %s, %s)",
            (code, amount, max_uses),
        )


async def get_promocode(code: str) -> dict | None:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM promocodes WHERE code = %s", (code,))
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_promocodes() -> list[dict]:
    async with get_connection() as db:
        async with db.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM promocodes")
            return [dict(row) for row in await cur.fetchall()]


async def delete_promocode(code: str) -> None:
    async with get_connection() as db:
        await db.execute("DELETE FROM promocodes WHERE code = %s", (code,))


async def use_promocode(user_id: int, code: str) -> dict:
    async with get_connection() as db:
        row = await (await db.execute(
            "SELECT id, amount, uses, max_uses FROM promocodes "
            "WHERE code = %s FOR UPDATE",
            (code,),
        )).fetchone()
        if not row:
            return {"success": False, "msg": "❌ Promokod topilmadi."}

        pid, amount, uses, max_uses = row
        if uses >= max_uses:
            return {
                "success": False,
                "msg": "❌ Promokod allaqachon ishlatib bo'lingan.",
            }

        existing_use = await (await db.execute(
            "SELECT 1 FROM promocode_uses WHERE user_id = %s AND promocode_id = %s",
            (user_id, pid),
        )).fetchone()
        if existing_use:
            return {
                "success": False,
                "msg": "❌ Siz bu promokodni oldin ishlatgansiz.",
            }

        await db.execute(
            "INSERT INTO promocode_uses (user_id, promocode_id) VALUES (%s, %s)",
            (user_id, pid),
        )
        await db.execute("UPDATE promocodes SET uses = uses + 1 WHERE id = %s", (pid,))
        await db.execute(
            "UPDATE users SET balance = balance + %s WHERE user_id = %s",
            (amount, user_id),
        )
        return {"success": True, "amount": amount}


async def export_backup() -> bytes:
    """Return a versioned JSON backup of all application data."""
    async with get_connection() as db:
        tables = {}
        for table in BACKUP_TABLES:
            async with db.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    f"SELECT * FROM {table} ORDER BY {_BACKUP_ORDER_BY[table]}"
                )
                tables[table] = [dict(row) for row in await cur.fetchall()]

    payload = {
        "format": "raqamchi-postgresql-backup",
        "version": 1,
        "tables": tables,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


async def restore_backup(payload: Any) -> None:
    """Atomically replace application tables from a validated JSON backup."""
    if not isinstance(payload, dict) or payload.get("format") != "raqamchi-postgresql-backup":
        raise ValueError("Unsupported database backup format.")
    if type(payload.get("version")) is not int or payload["version"] != 1:
        raise ValueError("Unsupported database backup version.")
    tables = payload.get("tables")
    if not isinstance(tables, dict) or set(tables) != set(BACKUP_TABLES):
        raise ValueError("Backup is missing one or more database tables.")
    if any(not isinstance(tables[table], list) for table in BACKUP_TABLES):
        raise ValueError("Backup table data must be a list.")

    async with get_connection() as db:
        for table in BACKUP_TABLES:
            async with db.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    f"SELECT column_name FROM information_schema.columns "
                    f"WHERE table_schema = current_schema() AND table_name = %s",
                    (table,),
                )
                allowed_columns = {row["column_name"] for row in await cur.fetchall()}
            if not allowed_columns:
                raise RuntimeError(f"Database table {table!r} does not exist.")

            for record in tables[table]:
                if (
                    not isinstance(record, dict)
                    or not record
                    or set(record) != allowed_columns
                ):
                    raise ValueError(f"Invalid record in backup table {table!r}.")

        for table in reversed(BACKUP_TABLES):
            await db.execute(f"DELETE FROM {table}")

        for table in BACKUP_TABLES:
            for record in tables[table]:
                columns = list(record)
                column_sql = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))
                values = tuple(record[column] for column in columns)
                await db.execute(
                    f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})",
                    values,
                )

        for table in _SEQUENCE_TABLES:
            await db.execute(
                f"""SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                ) FROM {table}"""
            )


async def restore_sqlite_backup(data: bytes) -> None:
    """Atomically replace application tables from a SQLite database file."""
    if not data:
        raise ValueError("SQLite backup is empty.")

    sqlite_db = sqlite3.connect(":memory:")
    try:
        try:
            sqlite_db.deserialize(data)
        except sqlite3.Error as error:
            raise ValueError("Invalid SQLite backup file.") from error

        sqlite_tables = {
            row[0]
            for row in sqlite_db.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        backup_data: dict[str, tuple[list[str], list[tuple[Any, ...]]]] = {}
        required_columns = {
            "users": {"user_id"},
            "purchases": {"id"},
            "deposits": {"id"},
            "channels": {"id"},
            "promocodes": {"id"},
            "promocode_uses": {"user_id", "promocode_id"},
            "join_requests": {"user_id", "chat_id"},
            "settings": {"key"},
        }

        for table in BACKUP_TABLES:
            if table not in sqlite_tables:
                raise ValueError(f"SQLite backup is missing table {table!r}.")

            columns = [
                row[1] for row in sqlite_db.execute(f"PRAGMA table_info({table})")
            ]
            if not required_columns[table].issubset(columns):
                raise ValueError(f"SQLite table {table!r} has an unsupported schema.")
            rows = sqlite_db.execute(f"SELECT * FROM {table}").fetchall()
            backup_data[table] = (columns, rows)
    finally:
        sqlite_db.close()

    async with get_connection() as db:
        for table, (columns, _) in backup_data.items():
            async with db.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = %s",
                    (table,),
                )
                allowed_columns = {row["column_name"] for row in await cur.fetchall()}
            if not allowed_columns or not set(columns).issubset(allowed_columns):
                raise ValueError(f"SQLite table {table!r} has unsupported columns.")

        for table in reversed(BACKUP_TABLES):
            await db.execute(f"DELETE FROM {table}")

        for table in BACKUP_TABLES:
            columns, rows = backup_data[table]
            if not rows:
                continue
            column_sql = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})"
            async with db.cursor() as cur:
                await cur.executemany(query, rows)

        for table in _SEQUENCE_TABLES:
            await db.execute(
                f"""SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                ) FROM {table}"""
            )
