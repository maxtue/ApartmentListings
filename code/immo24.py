from pathlib import Path
import argparse
from datetime import date
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json


class Immo24scrape:
    def __init__(self):
        pass

    def main(self):
        self.parse()
        self.set_vars()
        self.get_data()
        self.write_data()

    def set_vars(self):
        self.set_filepath()
        self.data = pd.DataFrame()
        self.page = 1
        self.broken_pages = []
        self.keep_running = True

    def get_data(self):
        while self.keep_running:
            print(f"Scraping results from page {self.page}.")
            try:
                self.get_links()
                self.get_pagedata()
            # catch html errors
            except requests.exceptions.RequestException as requests_error:
                print(str(requests_error))
                self.skip_page()
            # send e-mail for all other errors
            except Exception as e:
                print(str(e))
                self.write_data()
                raise SystemExit
            self.page += 1

    def skip_page(self):
        # Skip broken pages until there have been 5, then stop running
        print(f"Skipping page {self.page}.")
        self.broken_pages.append(self.page)
        if len(self.broken_pages) > 5:
            self.keep_running = False

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

    def set_filepath(self):
        self.filename = self.args.type + str(date.today()) + ".csv"
        # get absolute path to script directory and select data folder in parent directory
        self.savepath = str((Path(__file__).parent.absolute() / "../data/").resolve())
        self.filepath = self.savepath + "/" + self.filename

    def get_links(self):
        # scrape links to exposes from every individual result page
        self.links = []
        # get html page
        links_source = requests.get(
            "https://www.immobilienscout24.de/Suche/de/wohnung-"
            + self.args.type
            + "?pagenumber="
            + str(self.page)
        ).text
        # create soup object for parsing
        links_soup = BeautifulSoup(links_source, "lxml")
        # search through all hyperlink <a> containers
        for link_container in links_soup.find_all("a"):
            # check for expose links
            if r"/expose/" in str(link_container.get("href")):
                # cocatenate with homepage to get full link and append
                self.links.append(
                    "https://www.immobilienscout24.de" + link_container.get("href")
                )
            # use set function to remove duplicates
            self.links = list(set(self.links))

    def get_pagedata(self):
        for link in self.links:
            # get html page
            pagedata_source = requests.get(link).text
            # parse html page into soup object
            pagedata_soup = BeautifulSoup(pagedata_source, "lxml")
            # find html container in which data is stored
            pagedata_cont = pagedata_soup.head.find("script", type="text/javascript")
            # extract data which is stored in json style
            pagedata_json = pagedata_cont.text.split("keyValues = ")[1].split(";\n")[0]
            # convert json style data to python dictionary
            pagedata_dictionary = json.loads(pagedata_json)
            # put data into Pandas Dataframe
            pagedata_pandas = pd.DataFrame(
                pagedata_dictionary, index=[str(datetime.now())]
            )
            self.data = self.data.append(pagedata_pandas)

    def write_data(self):
        print(f"Writing data to {self.filepath}")
        with open(self.filepath, "w") as f:
            self.data.to_csv(
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
