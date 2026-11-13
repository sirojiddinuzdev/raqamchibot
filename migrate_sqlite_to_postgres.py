"""Import the existing SQLite database into an empty PostgreSQL database."""

import argparse
import asyncio
import logging
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import database as db

logger = logging.getLogger(__name__)

_TABLE_COLUMNS = {
    "users": (
        "user_id", "username", "full_name", "balance", "is_banned",
        "joined_at", "referred_by", "lang",
    ),
    "purchases": (
        "id", "user_id", "country", "country_name", "number", "hash_code",
        "price", "code", "password", "status", "bought_at", "original_price",
    ),
    "deposits": (
        "id", "user_id", "amount", "check_file", "admin_msg", "status",
        "created_at", "confirmed_at",
    ),
    "channels": ("id", "channel_id", "channel_name", "channel_link", "added_at"),
    "promocodes": ("id", "code", "amount", "uses", "max_uses", "expires_at"),
    "promocode_uses": ("user_id", "promocode_id"),
    "join_requests": ("user_id", "chat_id"),
    "settings": ("key", "value"),
}
_IMPORT_ORDER = (
    "users",
    "purchases",
    "deposits",
    "channels",
    "promocodes",
    "promocode_uses",
    "join_requests",
    "settings",
)
_DEFAULT_SETTINGS = {"card_number", "card_owner", "support_link", "welcome_msg"}
_SEQUENCE_TABLES = ("purchases", "deposits", "channels", "promocodes")
_ORDER_BY = {
    "users": "user_id",
    "purchases": "id",
    "deposits": "id",
    "channels": "id",
    "promocodes": "id",
    "promocode_uses": "user_id, promocode_id",
    "join_requests": "user_id, chat_id",
    "settings": "key",
}
_BATCH_SIZE = 500


def _read_sqlite_table(
    connection: sqlite3.Connection, table: str
) -> tuple[list[str], sqlite3.Cursor]:
    available = {
        row[1] for row in connection.execute(f"PRAGMA table_info({table})")
    }
    if not available:
        raise RuntimeError(f"SQLite table {table!r} is missing.")
    unsupported = available - set(_TABLE_COLUMNS[table])
    if unsupported:
        raise RuntimeError(
            f"SQLite table {table!r} has unsupported columns: "
            f"{', '.join(sorted(unsupported))}."
        )
    columns = [column for column in _TABLE_COLUMNS[table] if column in available]
    required = {
        "users": {"user_id"},
        "purchases": {"id"},
        "deposits": {"id"},
        "channels": {"id"},
        "promocodes": {"id"},
        "promocode_uses": {"user_id", "promocode_id"},
        "join_requests": {"user_id", "chat_id"},
        "settings": {"key"},
    }[table]
    if not required.issubset(columns):
        raise RuntimeError(f"SQLite table {table!r} has an unsupported schema.")
    cursor = connection.execute(f"SELECT {', '.join(columns)} FROM {table}")
    return columns, cursor


async def _verify_table(
    sqlite_db: sqlite3.Connection,
    postgres_db,
    table: str,
    columns: list[str],
) -> None:
    column_sql = ", ".join(columns)
    order_by = _ORDER_BY[table]
    source_cursor = sqlite_db.execute(
        f"SELECT {column_sql} FROM {table} ORDER BY {order_by}"
    )
    target_cursor = await postgres_db.execute(
        f"SELECT {column_sql} FROM {table} ORDER BY {order_by}"
    )

    if table == "settings":
        source_rows = source_cursor.fetchall()
        target_rows = await target_cursor.fetchall()
        target_by_key = {row[0]: row[1] for row in target_rows}
        if any(target_by_key.get(key) != value for key, value in source_rows):
            raise RuntimeError("SQLite settings values do not match PostgreSQL.")
        return

    while source_rows := source_cursor.fetchmany(_BATCH_SIZE):
        target_rows = await target_cursor.fetchmany(_BATCH_SIZE)
        if len(source_rows) != len(target_rows) or any(
            tuple(source_row) != tuple(target_row)
            for source_row, target_row in zip(source_rows, target_rows)
        ):
            raise RuntimeError(f"Data mismatch while verifying table {table!r}.")

    if await target_cursor.fetchmany(1):
        raise RuntimeError(f"PostgreSQL table {table!r} has unexpected rows.")


async def migrate(source: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"SQLite database not found: {source}")

    await db.init_db()
    try:
        sqlite_uri = f"{source.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(sqlite_uri, uri=True)) as sqlite_db:
            sqlite_db.row_factory = None
            source_counts = {
                table: sqlite_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in _IMPORT_ORDER
            }

            async with db.get_connection() as postgres_db:
                for table in _IMPORT_ORDER:
                    target_count = (await (await postgres_db.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    )).fetchone())[0]
                    if table == "settings":
                        existing_keys = {
                            row[0] for row in await (await postgres_db.execute(
                                "SELECT key FROM settings"
                            )).fetchall()
                        }
                        if not existing_keys.issubset(_DEFAULT_SETTINGS):
                            raise RuntimeError(
                                "PostgreSQL settings are not empty; refusing to merge "
                                "SQLite data into an already-used database."
                            )
                    elif target_count:
                        raise RuntimeError(
                            f"PostgreSQL table {table!r} is not empty; "
                            "migration only imports into a fresh database."
                        )

                for table in _IMPORT_ORDER:
                    columns, cursor = _read_sqlite_table(sqlite_db, table)
                    column_sql = ", ".join(columns)
                    placeholders = ", ".join(["%s"] * len(columns))
                    conflict_action = (
                        "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value"
                        if table == "settings"
                        else "ON CONFLICT DO NOTHING"
                    )
                    query = (
                        f"INSERT INTO {table} ({column_sql}) "
                        f"VALUES ({placeholders}) {conflict_action}"
                    )
                    async with postgres_db.cursor() as postgres_cursor:
                        while rows := cursor.fetchmany(_BATCH_SIZE):
                            await postgres_cursor.executemany(query, rows)

                for table in _SEQUENCE_TABLES:
                    await postgres_db.execute(
                        f"""SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE(MAX(id), 1),
                            MAX(id) IS NOT NULL
                        ) FROM {table}"""
                    )

                for table in _IMPORT_ORDER:
                    migrated_count = (await (await postgres_db.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    )).fetchone())[0]
                    if table == "settings":
                        if migrated_count < source_counts[table]:
                            raise RuntimeError(
                                "PostgreSQL settings count is lower than the SQLite source."
                            )
                    elif migrated_count != source_counts[table]:
                        raise RuntimeError(
                            f"Row count mismatch for {table}: SQLite has "
                            f"{source_counts[table]}, PostgreSQL has {migrated_count}."
                        )
                    columns, _ = _read_sqlite_table(sqlite_db, table)
                    await _verify_table(sqlite_db, postgres_db, table, columns)

        logger.info("SQLite data migration completed: %s", source_counts)
    finally:
        await db.close_db()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    default_path = Path(
        os.getenv("RAILWAY_VOLUME_MOUNT_PATH", ".")
    ) / "raqamchi.db"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=default_path,
        help="SQLite database file to import (default: %(default)s)",
    )
    args = parser.parse_args()
    asyncio.run(migrate(args.sqlite_path))


if __name__ == "__main__":
    main()
