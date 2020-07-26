import pandas as pd

from scraper import Scraper
import testhelpers as th


def test_parse_expose_local_kaufen():
    true_data = pd.read_csv(
        th.fullpath("test_kaufen.csv"),
        sep=";",
        decimal=",",
        encoding="utf-8",
        dtype=object,
    )
    scraper = Scraper()
    scraper.expose_html = th.get_local_html(th.fullpath("test_kaufen.html"))
    scraper.parse_expose_html()
    pd.testing.assert_frame_equal(scraper.data, true_data)
