import bs4 as bs
import urllib.request
import time
from datetime import datetime
import pandas as pd
import json


class Immo24scrape:
    def __init__(self, filename="rawdata.csv", savepath="./data/", numpages=1000):
        self.filename = filename
        self.savepath = savepath
        self.filepath = filename + savepath
        self.numpages = numpages

    def get_data(self):
        # iterate over result pages showing 20 results each
        for page in range(1, self.numpages):
            self.page = page
            print(f"Scraping results from page {self.page} of {self.numpages}.")
            # scrape data from every individual result page
            self.get_pagelinks()

    def get_pagelinks(self):
        self.links = []
        # use urllib.request and Beautiful soup to extract links
        soup = bs.BeautifulSoup(
            urllib.request.urlopen(
                "https://www.immobilienscout24.de/Suche/de/wohnung-kaufen?pagenumber="
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
        self.pagedata = pd.DataFrame
        # get data from every expose link
        for link in self.links():
            # use urllib.request and Beautiful soup to extract data
            soup = bs.BeautifulSoup(
                urllib.request.urlopen(
                    "https://www.immobilienscout24.de" + link
                ).read(),
                "lxml",
            )
            # extract features from data
            self.pagedata = pd.DataFrame(
                json.loads(
                    str(soup.find_all("script")).split("keyValues = ")[1].split("}")[0]
                    + str("}")
                ),
                index=[str(datetime.now())],
            )
            # extract expose texts from data
            self.pagedata["URL"] = str(link)
            expose_descriptions = []
            for description in soup.find_all("pre"):
                # extract text without html-markers
                expose_descriptions.append(description.text)
            # add column to dataframe
            self.pagedata["Exposes"] = str(expose_descriptions)

    def write_pagedata(self):
        print("Appending data of page {self.page} to {self.filepath}")
        self.pagedata.to_csv(
            self.filepath,
            # append data
            mode="a",
            # only create header if file is newly created
            header=self.filepath.tell() == 0,
            sep=";",
            decimal=",",
            encoding="utf-8",
            index_label="timestamp",
        )


if __name__ == "__main__":
    dataset = Immo24scrape()
    dataset.get_data()
