## ApartmentListings
Scrape and analyse Apartment listings for rent and sale from Germanys most popular housing website [Immobilienscout24.de](https://www.immobilienscout24.de/) with Python.


## Motivation
Sure, they offer some tools and data to analyse within their premium membership. But how much more fun would it be to have all the data yourself?

## Features
Visualize median rents and number of listings in a zip code or district

![](rent_timeseries_plot.png)

Check all current listings in a zip code or district ordered by rent per square meter  

![](rent_listings_table.png)

Compare median sale prices with median rent prices in all zip codes or districts



## Installation
After cloning the repository you can easily use Pipenv to set up a virtual environment wih all packages installed:
```
cd code/
pipenv install
```

## How to use?
If people like your project they’ll want to learn how they can use it. To do so include step by step guide to use your project.

## Main python packages used
 - Webscraper: BeautifulSoup4 and Requests
 - Data analysis: Pandas and Matplotlib
 - For a full list check the Pipfile!

## Tests
to be implemented

## Credits
Inspired by [this](https://statisquo.de/2017/11/16/immobilienscout24-mining-teil-1-worum-geht-es/) series of blog posts.

## License
GNU General Public License
