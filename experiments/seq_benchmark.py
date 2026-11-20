
import asyncio
import os
import time
from collections.abc import Awaitable, Callable

import psycopg
from dotenv import load_dotenv

from replay.idgen import SystemIdGen

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
WRITER_COUNT = 50
MAX_RETRIES = 100

id_gen = SystemIdGen()


async def write_event_max_retry(run_id: str) -> None:
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        autocommit=False,
    ) as conn:
        for attempt in range(MAX_RETRIES):
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT COALESCE(MAX(seq), 0) + 1
                        FROM events
                        WHERE run_id = %s
                        """,
                        (run_id,),
                    )
                    row = await cur.fetchone()
                    if row is None:
                        raise RuntimeError("MAX query returned no row")

                    seq = row[0]

                    await cur.execute(
                        """
                        INSERT INTO events
                            (run_id, seq, type, payload, created_at)
                        VALUES
                            (%s, %s, %s, %s, NOW())
                        """,
                        (run_id, seq, "BenchmarkEvent", "{}"),
                    )

                await conn.commit()
                return

            except psycopg.errors.UniqueViolation:
                await conn.rollback()

                if attempt == MAX_RETRIES - 1:
                    raise

                await asyncio.sleep(0.01 * (attempt + 1))


async def write_event_locked(run_id: str) -> None:
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        autocommit=False,
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT last_seq
                FROM runs
                WHERE id = %s
                FOR UPDATE
                """,
                (run_id,),
            )
            row = await cur.fetchone()

            if row is None:
                raise ValueError(f"Run not found: {run_id}")

            seq = row[0] + 1

            await cur.execute(
                """
                UPDATE runs
                SET last_seq = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (seq, run_id),
            )

            await cur.execute(
                """
                INSERT INTO events
                    (run_id, seq, type, payload, created_at)
                VALUES
                    (%s, %s, %s, %s, NOW())
                """,
                (run_id, seq, "BenchmarkEvent", "{}"),
            )

        await conn.commit()


async def run_benchmark(
    writer: Callable[[str], Awaitable[None]],
    run_id: str,
) -> float:
    start = time.perf_counter()

    await asyncio.gather(
        *(writer(run_id) for _ in range(WRITER_COUNT))
    )

    return time.perf_counter() - start


async def prepare_run(run_id: str) -> None:
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        autocommit=True,
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO runs (
                    id,
                    status,
                    agent_def,
                    input,
                    last_seq,
                    created_at,
                    updated_at
                )
                VALUES (%s, 'pending', '{}', '{}', 0, NOW(), NOW())
                """,
                (run_id,),
            )




async def verify_run(
    run_id: str,
    check_counter: bool,
) -> None:
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        autocommit=True,
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT COUNT(*), MIN(seq), MAX(seq), COUNT(DISTINCT seq)
                FROM events
                WHERE run_id = %s
                """,
                (run_id,),
            )
            row = await cur.fetchone()

            if row is None:
                raise RuntimeError("Event verification returned no row")

            count, min_seq, max_seq, distinct_count = row

            assert count == WRITER_COUNT
            assert min_seq == 1
            assert max_seq == WRITER_COUNT
            assert distinct_count == WRITER_COUNT

            if check_counter:
                await cur.execute(
                    "SELECT last_seq FROM runs WHERE id = %s",
                    (run_id,),
                )
                run_row = await cur.fetchone()

                if run_row is None:
                    raise RuntimeError("Run verification returned no row")

                last_seq = run_row[0]
                assert last_seq == max_seq, (
                    f"runs.last_seq={last_seq}, events.max_seq={max_seq}"
                )

    print(f"Verified: {count} events, seq 1..{max_seq}")



async def main() -> None:
    max_run_id = id_gen.new_id()
    locked_run_id = id_gen.new_id()

    await prepare_run(max_run_id)
    max_duration = await run_benchmark(
        write_event_max_retry,
        max_run_id,
    )
    await verify_run(max_run_id, check_counter=False)

    await prepare_run(locked_run_id)
    locked_duration = await run_benchmark(
        write_event_locked,
        locked_run_id,
    )
    await verify_run(locked_run_id, check_counter=True)

    print(f"MAX + retry: {max_duration:.3f}s")
    print(f"FOR UPDATE: {locked_duration:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
