from pathlib import Path
import traceback
import argparse
from datetime import date
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json


class Immo24scrape:

    """ Initialization methods """

    def __init__(self):
        pass

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
        # get absolute path to script directory and select data folder in parent directory
        self.savepath = str((Path(__file__).parent.absolute() / "../data/").resolve())
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

    def get_links(self):
        # scrape links to exposes from every individual result page
        self.links = []
        # get html page
        self.links_source = requests.get(
            "https://www.immobilienscout24.de/Suche/de/wohnung-"
            + self.args.type
            + "?pagenumber="
            + str(self.page)
        ).text
        self.parse_links_source()

    def parse_links_source(self):
        # create soup object for parsing
        links_soup = BeautifulSoup(self.links_source, "lxml")
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
        # exit if no expose links where found
        if not self.links:
            print("No links found on page " + str(self.page))
            self.smooth_exit()

    def get_linkdata(self):
        for link in self.links:
            try:
                # save link for error handling
                self.link = link
                # get html page
                pagedata_source = requests.get(link).text
                # parse html page into soup object
                pagedata_soup = BeautifulSoup(pagedata_source, "lxml")
                # find html container in which data is stored
                pagedata_cont = pagedata_soup.head.find(
                    "script", type="text/javascript"
                )
                # extract data which is stored in json style
                pagedata_json = pagedata_cont.text.split("keyValues = ")[1].split(
                    ";\n"
                )[0]
                # convert json style data to python dictionary
                pagedata_dictionary = json.loads(pagedata_json)
                # put data into Pandas Dataframe
                pagedata_pandas = pd.DataFrame(
                    pagedata_dictionary, index=[str(datetime.now())]
                )
                self.data = self.data.append(pagedata_pandas)
            except Exception:
                self.skip_link()

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

    """ Error handling methods """

    def skip_link(self):
        print("Error in link " + self.link + ":\n")
        traceback.print_exc()
        self.broken_links.append(self.link)
        if len(self.broken_links) > 100:
            print("Something is up, too many broken links: " + str(self.broken_links))
            self.smooth_exit()

    def smooth_exit(self):
        self.write_data()
        raise SystemExit


if __name__ == "__main__":
    dataset = Immo24scrape()
    dataset.main()
