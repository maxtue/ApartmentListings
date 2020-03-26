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
        self.set_filepath()
        self.run()

    def run(self):
        # iterate over all available result pages showing 20 results each
        self.page = 1
        self.broken_pages = []
        self.keep_running = True
        while self.keep_running:
            print(f"Scraping results from page {self.page}.")
            # check if pagenumber exists
            try:
                self.get_links()
                self.get_pagedata()
                self.write_pagedata()
            # catch urllib errors
            except False:
                self.skip_page()
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
        for paragraph in links_soup.find_all("a"):
            # get expose numbers
            if r"/expose/" in str(paragraph.get("href")):
                self.links.append(paragraph.get("href").split("#")[0])
            # use set function to only keep one link per expose
            self.links = list(set(self.links))

    def get_pagedata(self):
        self.pagedata = pd.DataFrame()
        for link in self.links:
            # get html page
            pagedata_source = requests.get(link).text
            # parse html page into soup object`
            pagedata_soup = BeautifulSoup(pagedata_source, "lxml")
            # find html element in which data is stored
            pagedata_element = pagedata_soup.head.find("script", type="text/javascript")
            # extract data which is stored in json style
            pagedata_json = pagedata_element.text.split("keyValues = ")[1].split("}")[
                0
            ] + str("}")
            # convert json style data to python dictionary
            pagedata_dictionary = json.loads(pagedata_json)
            # put data into Pandas Dataframe
            pagedata_pandas = pd.DataFrame(
                pagedata_dictionary, index=[str(datetime.now())]
            )
            self.pagedata = self.pagedata.append(pagedata_pandas)

    def write_pagedata(self):
        print(f"Writing data to {self.filepath}")
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
