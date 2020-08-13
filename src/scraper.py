import os
from pathlib import Path
import traceback
import argparse
from datetime import date
import random

from bs4 import BeautifulSoup
import pandas as pd
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--listingtype",
        choices=["mieten", "kaufen"],
        help="chose between 'mieten' and 'kaufen'",
        type=str,
        default="mieten",
    )
    args = parser.parse_args()
    return args


class Scraper:
    """ A web scraper for apartments on Immobilienscout.de """

    # Setter methods

    def __init__(self, listingtype="mieten"):
        self.listingtype = listingtype
        self.set_filepath()
        self.start_selenium_driver()
        self.data = pd.DataFrame()
        self.broken_exposes = []
        self.page = 1

    def set_filepath(self):
        filename = self.listingtype + str(date.today()) + ".csv"
        filedir = str((Path(__file__).parent.absolute() / "../data/").resolve())
        Path(filedir).mkdir(parents=True, exist_ok=True)
        self.filepath = os.path.join(filedir, filename)

    def start_selenium_driver(self):
        opts = Options()
        opts.binary_location = "/usr/bin/chromium"
        opts.headless = True
        self.driver = webdriver.Chrome(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=opts
        )

    # Getter methods

    def main(self):
        while self.page < 2:
            print(f"Scraping results from page {self.page}.")
            self.get_expose_links()
            self.parse_expose_links()
            self.check_expose_links()
            self.get_exposes()
            self.page += 1

    def get_expose_links(self):
        url = f"https://www.immobilienscout24.de/Suche/de/wohnung-{self.listingtype}?pagenumber={self.page}"
        self.driver.get(url)

    def parse_expose_links(self):
        self.exposes_links = []
        for link_container in self.driver.find_elements_by_tag_name("a"):
            if r"/expose/" in str(link_container.get_attribute("href")):
                self.exposes_links.append(
                    "https://www.immobilienscout24.de"
                    + link_container.get_attribute("href")
                )
        self.exposes_links = list(set(self.exposes_links))

    def check_expose_links(self):
        if not self.exposes_links:
            print("No exposes_links found on page " + str(self.page))
            self.smooth_exit()

    def get_exposes(self):
        for self.expose in self.exposes_links:
            try:
                self.get_expose_html()
                self.parse_expose_html()
            except Exception:
                self.skip_expose()

    def get_expose_html(self):
        self.expose_html = requests.get(self.expose).text

    def parse_expose_html(self):
        expose_soup = BeautifulSoup(self.expose_html, "lxml")
        expose_jsonlike = expose_soup.head.find("script", type="text/javascript")
        expose_json = str(expose_jsonlike).split("keyValues = ")[1].split(";\n")[0]
        expose_dictionary = json.loads(expose_json)
        expose_pandas = pd.DataFrame(expose_dictionary, index=[0])
        self.data = self.data.append(expose_pandas, ignore_index=True)

    def write_data(self):
        print(f"Writing data to {self.filepath}")
        self.data.to_csv(
            self.filepath, sep=";", decimal=",", encoding="utf-8", index=False
        )

    # Error handling methods

    def skip_expose(self):
        print("Error in expose " + self.expose + ":\n")
        traceback.print_exc()
        self.broken_exposes.append(self.expose)
        if len(self.broken_exposes) > 1000:
            print(
                "Something is up, too many broken exposes_links: "
                + str(self.broken_exposes)
            )
            self.smooth_exit()

    def smooth_exit(self):
        self.data = self.data.drop_duplicates(subset="obj_scoutId")
        self.write_data()
        raise SystemExit


if __name__ == "__main__":
    args = parse_args()
    scraper = Scraper(listingtype=args.listingtype)
    # scraper.main()
