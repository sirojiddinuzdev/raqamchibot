import asyncio
import os

import database as db


async def migrate() -> None:
    exchange_rate = int(os.getenv("EXCHANGE_RATE", "12000"))
    await db.init_db()
    try:
        async with db.get_connection() as connection:
            await connection.execute(
                "UPDATE users SET balance = balance * %s", (exchange_rate,)
            )
            rows = await (await connection.execute(
                "SELECT key, value FROM settings WHERE key LIKE 'country_%'"
            )).fetchall()
            for key, value in rows:
                try:
                    new_price = int(float(value) * exchange_rate)
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"Invalid country price in setting {key!r}"
                    ) from error
                await connection.execute(
                    "UPDATE settings SET value = %s WHERE key = %s",
                    (str(new_price), key),
                )
            await connection.execute(
                "UPDATE purchases SET price = price * %s", (exchange_rate,)
            )
            await connection.execute(
                "UPDATE deposits SET amount = amount * %s", (exchange_rate,)
            )
    finally:
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(migrate())
