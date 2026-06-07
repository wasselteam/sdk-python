from typing import override

from wassel_sdk import http, redis
from wassel_sdk.redis import RedisArgument_Str, RedisValue_BulkString

CONNECTION_STRING = "redis://localhost:6379"


class HttpHandler(http.HttpHandler):
    @override
    def handle(self, request: http.Request) -> http.Response:
        _ = request
        try:
            s = make_query()
            body = f"my:value = {s}".encode()
            return http.Response(body=body)
        except Exception as e:
            return http.Response(body=str(e).encode(), status=500)


def make_query() -> str:
    config = redis.ConnectionConfig(CONNECTION_STRING)
    conn = redis.Connection.open(config)
    conn.execute("SET", [RedisArgument_Str("my:value"), RedisArgument_Str("Hello")])
    s = conn.execute("GET", [RedisArgument_Str("my:value")])
    assert isinstance(s, RedisValue_BulkString)
    return s.value.decode()
