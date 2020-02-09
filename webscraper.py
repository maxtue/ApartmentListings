import bs4 as bs
import urllib.request
import time
from datetime import datetime
import pandas as pd
import json

for seite in range(1, 1600):

    print("Loop " + str(seite) + " startet.")

    df = pd.DataFrame()
    l = []

    try:

        soup = bs.BeautifulSoup(
            urllib.request.urlopen(
                "https://www.immobilienscout24.de/Suche/de/wohnung-kaufen?pagenumber="
                + str(seite)
            ).read(),
            "lxml",
        )
        print(
            "Aktuelle Seite: "
            + "https://www.immobilienscout24.de/Suche/de/wohnung-kaufen?pagenumber="
            + str(seite)
        )
        for paragraph in soup.find_all("a"):

            if r"/expose/" in str(paragraph.get("href")):
                l.append(paragraph.get("href").split("#")[0])

            l = list(set(l))

        for item in l:

            try:

                soup = bs.BeautifulSoup(
                    urllib.request.urlopen(
                        "https://www.immobilienscout24.de" + item
                    ).read(),
                    "lxml",
                )

                data = pd.DataFrame(
                    json.loads(
                        str(soup.find_all("script"))
                        .split("keyValues = ")[1]
                        .split("}")[0]
                        + str("}")
                    ),
                    index=[str(datetime.now())],
                )

                data["URL"] = str(item)

                beschreibung = []

                for i in soup.find_all("pre"):
                    beschreibung.append(i.text)

                data["beschreibung"] = str(beschreibung)

                df = df.append(data)

            except Exception as e:
                print(str(datetime.now()) + ": " + str(e))
                l = list(filter(lambda x: x != item, l))
                print("ID " + str(item) + " entfernt.")
        print("Exportiert CSV")
        df.to_csv(
            ".../rohdaten/"
            + str(datetime.now())[:19].replace(":", "").replace(".", "")
            + ".csv",
            sep=";",
            decimal=",",
            encoding="utf-8",
            index_label="timestamp",
        )

        print("Loop " + str(seite) + " endet.\n")

    except Exception as e:
        print(str(datetime.now()) + ": " + str(e))

print("FERTIG!")

