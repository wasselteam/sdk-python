from typing import override

from wassel_sdk import http
from wassel_sdk.http import (
    Err,
    Fields,
    IncomingBody,
    OutgoingRequest,
    StreamError_Closed,
)


class HttpHandler(http.HttpHandler):
    @override
    def handle(self, request: http.Request) -> http.Response:
        if not request.path.startswith("/todos/"):
            return http.Response(status=404)

        try:
            path = request.path.removeprefix("/todos/")
            id = int(path)
            url = f"https://jsonplaceholder.typicode.com/todos/{id}"
            req = OutgoingRequest(Fields())
            res = http.client.send(url, req)
            status = res.status()
            body = read_body(res.consume())

            return http.Response(status=status, body=body)

        except ValueError as e:
            return http.Response(status=400, body=str(e).encode())

        except Exception as e:
            return http.Response(status=500, body=str(e).encode())


STREAM_READ_COUNT = 1024 * 64


def read_body(body: IncomingBody) -> bytes:
    buf = bytes()
    try:
        with body.stream() as stream:
            while True:
                b = stream.blocking_read(STREAM_READ_COUNT)
                buf = buf + b
    except Err as e:
        if isinstance(e.value, StreamError_Closed):
            return buf
        else:
            raise e
    finally:
        IncomingBody.finish(body)
