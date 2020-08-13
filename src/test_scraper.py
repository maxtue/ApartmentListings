import pytest

from scraper import Scraper
import testhelpers


def test_init_scraper_kaufen():
    scraper = Scraper(listingtype="kaufen")
    assert True


@pytest.fixture
def fixture_init_scraper_kaufen():
    scraper = Scraper(listingtype="kaufen")
    return scraper


def test_get_expose_links_html_kaufen(fixture_init_scraper_kaufen):
    scraper = fixture_init_scraper_kaufen
    scraper.get_expose_links()
    assert True


def test_expose_links_html_kaufen_are_string(fixture_get_expose_links_html_kaufen):
    scraper = fixture_get_expose_links_html_kaufen
    assert isinstance(scraper.exposes_links_html, str)


def test_parse_expose_links_html_kaufen(fixture_get_expose_links_html_kaufen):
    scraper = fixture_get_expose_links_html_kaufen
    scraper.parse_expose_links_html()
    assert True


@pytest.fixture
def fixture_parse_expose_links_html_kaufen(fixture_get_expose_links_html_kaufen):
    scraper = fixture_get_expose_links_html_kaufen
    scraper.parse_expose_links()
    return scraper


def test_check_expose_links(fixture_parse_expose_links_html_kaufen):
    scraper = fixture_parse_expose_links_html_kaufen
    assert scraper.exposes_links


def test_check_expose_links_kaufen():
    assert True
