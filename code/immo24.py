import bs4 as bs
import urllib.request
from datetime import date
from datetime import datetime
import pandas as pd
import json


class Immo24scrape:
    def __init__(
        self, filename="rawdata" + str(date.today()) + ".csv", savepath="../data/",
    ):
        self.filename = filename
        self.savepath = savepath
        self.filepath = savepath + filename

    def scrape_data(self):
        # iterate over all available result pages showing 20 results each
        self.page = 1
        while True:
            print(f"Scraping results from page {self.page}.")
            # check if pagenumber is available
            try:
                self.get_pagelinks()
                self.get_pagedata()
                self.write_pagedata()
            # catch urllib error after last page has been reached
            except IOError:
                print(f"Number of scraped pages today: {self.page}")
                break
            self.page += 1

    def get_pagelinks(self):
        # scrape links to exposes from every individual result page
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
            # extract features
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
    dataset.scrape_data()
