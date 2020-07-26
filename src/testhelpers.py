import os
from pathlib import Path

import requests
from requests_testadapter import Resp

from scraper import Scraper


class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, "rb") as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)
            return r

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        return self.build_response_from_file(request)


def fullpath(filename):
    return os.path.join(Path(__file__).parent.absolute(), filename)


def get_local_html(filename):
    requests_session = requests.session()
    requests_session.mount("file://", LocalFileAdapter())
    html_file = requests_session.get("file://" + fullpath(filename)).text
    return html_file


def save_local_csv():
    scraper = Scraper()
    scraper.expose_html = get_local_html("test_kaufen.html")
    scraper.parse_expose_html()
    scraper.data.to_csv(
        fullpath("test_kaufen.csv"), sep=";", decimal=",", encoding="utf-8", index=False
    )
