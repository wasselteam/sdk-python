import pathlib
from typing import override

from jinja2 import DictLoader, Environment, select_autoescape

from wassel_sdk import http


def read_entire_file(path: str) -> str:
    final_path = pathlib.Path(__file__).parent.resolve().joinpath(path)
    with open(final_path, "r") as file:
        return file.read()


templates = {
    "index.html": read_entire_file("templates/index.html"),
}

env = Environment(
    loader=DictLoader(templates),
    autoescape=select_autoescape(),
)


class HttpHandler(http.HttpHandler):
    @override
    def handle(self, request: http.Request) -> http.Response:
        _ = request
        template = env.get_template("index.html")
        html = template.render().encode("utf-8")
        return http.Response(
            body=html, headers={"content-type": b"text/html; charset=utf-8"}
        )
