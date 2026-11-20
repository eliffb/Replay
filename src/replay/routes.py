import psycopg
from fastapi import APIRouter, HTTPException
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from replay.clock import SystemClock
from replay.config import DATABASE_URL
from replay.idgen import SystemIdGen

router = APIRouter()
id_gen = SystemIdGen()
clock = SystemClock()


class CreateRunRequest(BaseModel):
    agent_def: dict[str, object]
    input: dict[str, object] = Field(default_factory=dict)


@router.post("/runs", status_code=201)
def create_run(request: CreateRunRequest) -> dict[str, str]:
    if DATABASE_URL is None:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")

    run_id = id_gen.new_id()
    now = clock.now()

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO runs (
                        id, status, agent_def, input,
                        last_seq, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        run_id, "pending", Jsonb(request.agent_def),
                        Jsonb(request.input), 0, now, now,
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO events (
                        run_id, seq, type, schema_version, payload, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        run_id, 1, "RunCreated", 1,
                        Jsonb({
                            "event_type": "RunCreated",
                            "run_id": str(run_id),
                            "schema_version": 1,
                            "input": request.input,
                        }),
                        now,
                    ),
                )

                cur.execute(
                    "UPDATE runs SET last_seq = 1 WHERE id = %s",
                    (run_id,),
                )

        return {"id": str(run_id), "status": "pending"}

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not create run",
        ) from exc


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, object]:
    if DATABASE_URL is None:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, status, agent_def, input,
                           last_seq, created_at, updated_at
                    FROM runs
                    WHERE id = %s
                    """,
                    (run_id,),
                )
                row = cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Run not found")

        return {
            "id": str(row[0]),
            "status": row[1],
            "agent_def": row[2],
            "input": row[3],
            "last_seq": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve run",
        ) from exc


@router.get("/runs/{run_id}/events")
def get_run_events(run_id: str) -> list[dict[str, object]]:
    if DATABASE_URL is None:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM runs WHERE id = %s",
                    (run_id,),
                )
                run_exists = cur.fetchone()

                if run_exists is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Run not found",
                    )

                cur.execute(
                    """
                    SELECT seq, type, schema_version, payload, created_at
                    FROM events
                    WHERE run_id = %s
                    ORDER BY seq ASC
                    """,
                    (run_id,),
                )
                rows = cur.fetchall()

        return [
            {
                "seq": row[0],
                "type": row[1],
                "schema_version": row[2],
                "payload": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve run events",
        ) from exc