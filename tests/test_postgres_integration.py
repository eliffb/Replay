import psycopg
from testcontainers.community.postgres import PostgresContainer


def test_postgres_connection_and_query() -> None:
    with PostgresContainer("postgres:16") as postgres:
        connection = psycopg.connect(
            host=postgres.get_container_host_ip(),
            port=postgres.get_exposed_port(5432),
            dbname=postgres.dbname,
            user=postgres.username,
            password=postgres.password,
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE test_items (id SERIAL PRIMARY KEY, name TEXT)"
                )
                cursor.execute(
                    "INSERT INTO test_items (name) VALUES (%s) RETURNING name",
                    ("Replay",),
                )
                result = cursor.fetchone()

            assert result is not None
            assert result[0] == "Replay"
        finally:
            connection.close()