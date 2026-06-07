from wassel_sdk.wit import exports
from wassel_sdk.wit.imports.wasi_http_types_0_2_10 import *
from wassel_sdk.wit.imports.wasi_io_streams_0_2_10 import (
    Err,
    StreamError_Closed,
    StreamError_LastOperationFailed,
)
from wassel_sdk.wit.imports import wassel_http_client_http_client as client

from typing import override
from abc import abstractmethod
from dataclasses import dataclass, field
import traceback

GET = "GET"
HEAD = "HEAD"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"
CONNECT = "CONNECT"
OPTIONS = "OPTIONS"
TRACE = "TRACE"
PATCH = "PATCH"


@dataclass
class Request:
    path: str
    method: str
    headers: dict[str, bytes]
    body: bytes | None


@dataclass
class Response:
    status: int = 200
    headers: dict[str, bytes] = field(default_factory=dict)
    body: bytes | None = None


class HttpHandler(exports.HttpHandler):
    @override
    def handle_request(
        self, request: IncomingRequest, response_out: ResponseOutparam
    ) -> None:
        res = None
        try:
            # TODO: convert method to string
            path = request.path_with_query() or "/"
            method = request.method()
            headers = dict(request.headers().entries())
            body = read_body(request)

            req = Request(path=path, method=method, headers=headers, body=body)
            res = self.handle(req)

        except Exception as e:
            body_s = f"Unhandled exception: {e}\n{traceback.format_exc()}"
            write_response(response_out, 500, bytes(body_s, "utf-8"))
            return

        # TODO: res.headers
        # TODO: allow body to be stream and str
        write_response(response_out, res.status, res.body, res.headers)

    @abstractmethod
    def handle(self, request: Request) -> Response:
        raise NotImplementedError("HttpHandler.handle")


STREAM_READ_COUNT = 1024 * 64


def write_response(
    out: http.ResponseOutparam,
    status: int | None = None,
    body_bytes: bytes | None = None,
    headers: dict[str, bytes] | None = None,
) -> None:
    if status is None:
        status = 200

    if headers is None:
        headers = {}

    res = OutgoingResponse(Fields.from_list(list(headers.items())))
    res.set_status_code(status)

    if body_bytes is not None:
        body = res.body()
        with body.write() as stream:
            stream.write(body_bytes)
        OutgoingBody.finish(body, None)

    ResponseOutparam.set(out, Ok(res))


def read_body(request: IncomingRequest) -> bytes | None:
    body = None
    try:
        body = request.consume()
    except Err:
        return None

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
