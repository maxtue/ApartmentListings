from pathlib import Path
import traceback
import argparse
from datetime import date
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json


class Immo24:

    """ Initialization methods """

    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--type",
            choices=["mieten", "kaufen"],
            help="chose between 'mieten' and 'kaufen'",
            type=str,
            default="mieten",
        )
        self.args = parser.parse_args()

    def set_vars(self):
        self.set_filepath()
        self.data = pd.DataFrame()
        self.broken_links = []
        self.page = 1

    def set_filepath(self):
        self.filename = self.args.type + str(date.today()) + ".csv"
        self.savepath = str((Path(__file__).parent.absolute() / "../data/").resolve())
        Path(self.savepath).mkdir(parents=True, exist_ok=True)
        self.filepath = self.savepath + "/" + self.filename

    """ Main methods """

    def main(self):
        self.parse()
        self.set_vars()
        self.get_data()

    def get_data(self):
        while True:
            print(f"Scraping results from page {self.page}.")
            self.get_links()
            self.get_linkdata()
            self.page += 1
            if self.page == 2:
                self.smooth_exit()

    def get_links(self):
        self.links = []
        self.links_source = requests.get(
            "https://www.immobilienscout24.de/Suche/de/wohnung-"
            + self.args.type
            + "?pagenumber="
            + str(self.page)
        ).text
        self.parse_links_exposes()

    def parse_links_exposes(self):
        links_soup = BeautifulSoup(self.links_source, "lxml")
        for link_container in links_soup.find_all("a"):
            if r"/expose/" in str(link_container.get("href")):
                self.links.append(
                    "https://www.immobilienscout24.de" + link_container.get("href")
                )
        if not self.links:
            print("No exposes found on page " + str(self.page))
            self.smooth_exit()

    def get_linkdata(self):
        for link in self.links:
            self.link = link
            try:
                self.get_linkvalues()
                self.data = self.data.append(self.pagedata_pandas)
            except Exception:
                self.skip_link()

    def get_linkvalues(self):
        self.pagedata_source = requests.get(self.link).text
        self.pagedata_soup = BeautifulSoup(self.pagedata_source, "lxml")
        self.pagedata_values = self.pagedata_soup.head.find(
            "script", type="text/javascript"
        )
        self.pagedata_json = (
            str(self.pagedata_values).split("keyValues = ")[1].split(";\n")[0]
        )

        self.pagedata_dictionary = json.loads(self.pagedata_json)
        self.pagedata_pandas = pd.DataFrame(
            self.pagedata_dictionary, index=[str(datetime.now())]
        )

    def write_data(self):
        print(f"Writing data to {self.filepath}")
        with open(self.filepath, "w") as f:
            self.data.to_csv(
                f, sep=";", decimal=",", encoding="utf-8", index_label="timestamp",
            )

    """ Error handling methods """

    def skip_link(self):
        print("Error in link " + self.link + ":\n")
        traceback.print_exc()
        self.broken_links.append(self.link)
        if len(self.broken_links) > 100:
            print("Something is up, too many broken links: " + str(self.broken_links))
            self.smooth_exit()

    def smooth_exit(self):
        self.data = self.data.drop_duplicates(subset="obj_scoutId")
        self.write_data()
        raise SystemExit


if __name__ == "__main__":
    dataset = Immo24()
    dataset.main()