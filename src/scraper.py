from pathlib import Path
import traceback
import argparse
from datetime import date
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json


class Scraper:
    """ A web scraper for apartments on Immobilienscout.de """

    # Setter methods

    def __init__(self):
        self.parse_argparse()
        self.set_filepath()
        self.data = pd.DataFrame()
        self.broken_exposes = []
        self.page = 1

    def parse_argparse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--type",
            choices=["mieten", "kaufen"],
            help="chose between 'mieten' and 'kaufen'",
            type=str,
            default="mieten",
        )
        self.args = parser.parse_args()

    def set_filepath(self):
        filename = self.args.type + str(date.today()) + ".csv"
        savepath = str((Path(__file__).parent.absolute() / "../data/").resolve())
        Path(savepath).mkdir(parents=True, exist_ok=True)
        self.filepath = savepath + "/" + filename

    # Getter methods

    def main(self):
        while True:
            print(f"Scraping results from page {self.page}.")
            self.get_expose_links()
            self.get_expose_data()
            self.page += 1

    def get_expose_links(self):
        self.exposes_page = requests.get(
            "https://www.immobilienscout24.de/Suche/de/wohnung-"
            + self.args.type
            + "?pagenumber="
            + str(self.page)
        ).text
        self.parse_exposes_page()

    def parse_exposes_page(self):
        self.exposes = []
        exposes_soup = BeautifulSoup(self.exposes_page, "lxml")
        for expose_container in exposes_soup.find_all("a"):
            if r"/expose/" in str(expose_container.get("href")):
                self.exposes.append(
                    "https://www.immobilienscout24.de" + expose_container.get("href")
                )
        self.exposes = list(set(self.exposes))
        if not self.exposes:
            print("No exposes found on page " + str(self.page))
            self.smooth_exit()

    def get_expose_data(self):
        for self.expose in self.exposes:
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
        expose_pandas = pd.DataFrame(expose_dictionary, index=[str(datetime.now())])
        self.data = self.data.append(expose_pandas)

    def write_data(self):
        print(f"Writing data to {self.filepath}")
        with open(self.filepath, "w") as f:
            self.data.to_csv(
                f, sep=";", decimal=",", encoding="utf-8", index_label="timestamp",
            )

    # Error handling methods

    def skip_expose(self):
        print("Error in expose " + self.expose + ":\n")
        traceback.print_exc()
        self.broken_exposes.append(self.expose)
        if len(self.broken_exposes) > 1000:
            print(
                "Something is up, too many broken exposes: " + str(self.broken_exposes)
            )
            self.smooth_exit()

    def smooth_exit(self):
        self.data = self.data.drop_duplicates(subset="obj_scoutId")
        self.write_data()
        raise SystemExit


if __name__ == "__main__":
    scraper = Scraper()
    scraper.main()
