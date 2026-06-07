from typing import override

from wassel_sdk import http, postgres

CONNECTION_STRING: str = (
    "host=127.0.0.1 "
    "port=25432 "
    "user=wassel-test "
    "password=wassel-test "
    "dbname=wassel-test"
)


class HttpHandler(http.HttpHandler):
    @override
    def handle(self, request: http.Request) -> http.Response:
        _ = request
        try:
            num = make_query()
            body = f"SELECT 1 + 1 = {num}"
            return http.Response(body=bytes(body, "utf-8"))
        except Exception as e:
            return http.Response(body=bytes(str(e), "utf-8"), status=500)


def make_query() -> int:
    config = postgres.ConnectionConfig(CONNECTION_STRING)
    conn = postgres.Connection.open(config)
    rows = conn.query(
        "SELECT $1 + $2", [postgres.Value_Int32(5), postgres.Value_Int32(6)]
    )
    num = rows.rows[0][0]
    assert isinstance(num, postgres.Value_Int32)
    return num.value
