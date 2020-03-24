from pathlib import Path
import argparse
from datetime import date
from datetime import datetime

import bs4 as bs
import urllib.request
from urllib.error import URLError, HTTPError
import pandas as pd
import json


class Immo24scrape:
    def __init__(self):
        pass

    def main(self):
        self.parse()
        # iterate over all available result pages showing 20 results each
        self.page = 1
        while True:
            print(f"Scraping results from page {self.page}.")
            # check if pagenumber exists
            try:
                self.get_pagelinks()
                self.get_pagedata()
                self.write_pagedata()
            # catch urllib error after last page has been reached
            except (URLError, HTTPError):
                print(f"Number of scraped pages today: {self.page}")
                break
            self.page += 1

    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--type",
            choices=["mieten", "kaufen"],
            help="chose 'mieten' or 'kaufen'",
            type=str,
            default="mieten",
        )
        self.args = parser.parse_args()

    def set_filepath(self):
        self.filename = self.args.type + str(date.today()) + ".csv"
        # get absolute path to script directory and select data folder in parent directory
        self.savepath = str((Path(__file__).parent.absolute() / "../data/").resolve())
        self.filepath = self.savepath + "/" + self.filename

    def get_pagelinks(self):
        # scrape links to exposes from every individual result page
        self.links = []
        # use urllib.request and Beautiful soup to extract links
        soup = bs.BeautifulSoup(
            urllib.request.urlopen(
                "https://www.immobilienscout24.de/Suche/de/wohnung-"
                + self.args.typ
                + "?pagenumber="
                + str(self.page)
            ).read(),
            "lxml",
        )
        # find all paragraphs in html-page
        for paragraph in soup.find_all("a"):
            # get expose numbers
            if r"/expose/" in str(paragraph.get("href")):
                self.links.append(paragraph.get("href").split("#")[0])
            # use set function to remove duplicates (?)
            self.links = list(set(self.links))

    def get_pagedata(self):
        self.pagedata = pd.DataFrame()
        # get data from every expose link
        for link in self.links:
            # use urllib.request and Beautiful soup to extract data
            soup = bs.BeautifulSoup(
                urllib.request.urlopen(
                    "https://www.immobilienscout24.de" + link
                ).read(),
                "lxml",
            )
            # extract features into Pandas Dataframe with json loader
            linkdata = pd.DataFrame(
                json.loads(
                    str(soup.find_all("script")).split("keyValues = ")[1].split("}")[0]
                    + str("}")
                ),
                index=[str(datetime.now())],
            )
            # save URL as unique identifier
            linkdata["URL"] = str(link)
            self.pagedata = self.pagedata.append(linkdata)

    def write_pagedata(self):
        print(f"Appending data of page {self.page} to {self.filepath}")
        with open(self.filepath, "a") as f:
            self.pagedata.to_csv(
                f,
                # only create header if file is newly created
                header=f.tell() == 0,
                sep=";",
                decimal=",",
                encoding="utf-8",
                index_label="timestamp",
            )


if __name__ == "__main__":
    dataset = Immo24scrape()
    dataset.main()
