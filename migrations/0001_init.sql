
CREATE TABLE runs (
    id           uuid PRIMARY KEY,
    status       text NOT NULL,
    agent_def    jsonb NOT NULL,
    input        jsonb,
    last_seq     int NOT NULL DEFAULT 0,
    created_at   timestamptz NOT NULL,
    updated_at   timestamptz NOT NULL
);

CREATE TABLE steps (
    run_id       uuid REFERENCES runs(id),
    step_no      int NOT NULL,
    status       text NOT NULL,
    attempts     int NOT NULL DEFAULT 0,
    PRIMARY KEY (run_id, step_no)
);

CREATE TABLE events (
    run_id         uuid REFERENCES runs(id),
    seq            int NOT NULL,
    type           text NOT NULL,
    schema_version int NOT NULL DEFAULT 1,
    payload        jsonb NOT NULL,
    created_at     timestamptz NOT NULL,
    PRIMARY KEY (run_id, seq)
);
