from bs4 import BeautifulSoup
import datetime
import http
import logging
import numpy as np
import pandas as pd
import random
import re
import selenium
from selenium import webdriver
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')


class BookScraper:

    def __init__(self):

        extension = "_2_jan_00"
        self.book_file = f"files/book_data{extension}.csv"
        self.book_mapping_file = f"files/book_mapping{extension}.csv"
        self.logger = logging.getLogger(__name__)
        self.amazon_url = "https://www.amazon.com"

        try:
            self.books = pd.read_csv(self.book_file)
            self.books = self.books[~self.books["url"].duplicated()].copy()
            self.scraped_urls = set(self.books["url"].unique())
            self.logger.info(f"Found scraped data for {len(self.books)} books.")
        except FileNotFoundError:
            self.books = pd.DataFrame()
            self.scraped_urls = set()

        try:
            self.book_mapping = pd.read_csv(self.book_mapping_file)
            self.book_mapping = self.book_mapping[
                (~self.book_mapping[["title", "main_title"]].duplicated())].copy()
            self.urls = self.book_mapping["url"].to_list()
            disjoint_set = set(self.urls).difference(self.scraped_urls)
            self.logger.info(f"Number of URLs found and not scraped is {len(disjoint_set)}.")
        except FileNotFoundError:
            self.book_mapping = pd.DataFrame()
            self.urls = []

        self.book_info = {}
        self.limit = 10_000

    def make_soup(self, url: str = None) -> BeautifulSoup:
        link = self.amazon_url + url
        self.book_info["url"] = url

        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        try:
            driver.get(link)
            source = driver.page_source
            driver.close()
            soup = BeautifulSoup(source, features="html.parser")
        except (http.client.IncompleteRead, selenium.common.exceptions.WebDriverException):
            return
        return soup

    def extract_info_from_soup(self, soup: BeautifulSoup):

        # book title
        main_title = [item.strip() for item in soup.find(
            'span', {'id': 'productTitle'}
        )][0]
        self.book_info["title"] = main_title

        # book author
        author = [item for item in soup.find_all(
            'a',
            {'class': "a-link-normal contributorNameID"}
        )]
        try:
            self.book_info["author"] = author[0].text
        except IndexError:
            self.book_info["author"] = ""

        num_reviews = [item for item in soup.find_all('a', {"id": "acrCustomerReviewLink"})]
        try:
            self.book_info["num_reviews"] = float(num_reviews[0].text.strip().split()[0].replace(',', ''))
        except IndexError:
            self.book_info["num_reviews"] = np.nan

        try:
            rating = ([item for item in soup.find_all(
                'span',
                {"class": "reviewCountTextLinkedHistogram noUnderline"}
            )])[0].text.strip().replace(' out of 5 stars', '')
        except IndexError:
            rating = np.nan
        self.book_info["rating"] = float(rating)

        auth_about_class = "a-cardui-content a-cardui-uninitialized"
        try:
            about_auth = [item for item in soup.find_all("div", {"class": auth_about_class})][0].text
        except IndexError:
            about_auth = ""
        self.book_info["about_author"] = about_auth

        try:
            book_description = [item for item in soup.find_all(
                "div",
                {"data-a-expander-name": "book_description_expander"}
            )][0].text
        except IndexError:
            book_description = ""
        self.book_info["book_description"] = book_description

        # rankings in various categories. These can be used perhaps in clustering.
        try:
            rankings = [item for item in soup.find_all(
                "ul",
                {"class": "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"}
            )][1]
            rankings = [item.strip() for item in rankings.text.strip().replace(
                'Best Sellers Rank:', '').strip().split('#') if item.strip()]
            remove_str = '(See Top 100 in Books)'

            ranking_dict = {}
            for item in rankings:
                item = item.replace(remove_str, '').strip()
                val, key = item[0], item[2:]
                val = val.replace(",", "").replace("#", "")
                ranking_dict[key.strip()] = int(val.strip())
            self.book_info["rankings"] = ranking_dict
        except IndexError:
            self.book_info["rankings"] = {}

        # metadata like publisher, book length, weight, publication date etc.
        try:
            metadata = [item for item in soup.find_all(
                "ul",
                {"class": "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"}
             )][0].text.replace('\n', ' ').replace('\u200f', ' ').replace('\u200e', '')

            metadata = (re.split(': |\n|   |!|\+', metadata))
            metadata = [item.strip() for item in metadata if item.strip()]
            metadata_dict = {}

            i = 0
            if len(metadata) >= 2:
                while i < len(metadata) - 1:
                    metadata_dict[metadata[i]] = metadata[i + 1]
                    i += 2

            for k, v in metadata_dict.items():
                if 'edition' in v:
                    dttime_string = v.split('edition')[-1].strip()
                    self.book_info["publication_date"] = self.string_time_to_datetime(dttime_string)
                self.book_info[k] = v
        except IndexError:
            self.book_info["publication_date"] = datetime.date.fromisoformat('1400-01-01')

        books = [item for item in soup.find_all("div", {"class": "p13n-sc-uncoverable-faceout"})]

        urls = []
        for book in books:
            url = book.a["href"]
            idx = url.find("ref=")
            urls.append(url[:idx])

        titles = [book.img["alt"] for book in books]
        if len(titles) < len(urls):
            titles += [''] * int(np.ceil([len(urls) - len(titles)]))
        try:
            authors = [book.find(
                "div",
                {"class": "_cDEzb_p13n-sc-css-line-clamp-1_2o7X6"}
            ).text for book in books]
        except AttributeError:
            try:
                authors = [item.text for item in soup.find_all(
                    "div",
                    {"class": "_cDEzb_p13n-sc-css-line-clamp-1_2o7X6"}
                )]
            except AttributeError:
                authors = []
        if len(authors) < len(urls):
            authors += [''] * int(np.ceil([len(urls) - len(authors)]))

        mapped_books = []
        for title, author, url in zip(titles, authors, urls):
            mapped_books.append([title, author, url])
            self.urls.append(url)

        mapped_books = pd.DataFrame(mapped_books, columns=["title", "author", "url"])
        if mapped_books.any().any():
            mapped_books.loc[:, "main_title"] = main_title

        return mapped_books, pd.DataFrame.from_dict(self.book_info, orient="index").T

    def string_time_to_datetime(self, date_string: str) -> datetime:

        date_string = date_string.replace('(', '').replace(')', '').replace(',', '')
        fmt = '%B %d %Y'
        try:
            date = datetime.datetime.strptime(date_string, fmt)
        except ValueError:
            date = datetime.date.fromisoformat('1400-01-01')
        return date

    def scrape_for_books(self):

        counter = len(self.scraped_urls)
        self.amazon_url = "https://www.amazon.com"

        # start with this URL if nothing scraped yet.
        url = "/Future-Superhuman-transhuman-make-break/dp/1742236758"

        while counter < self.limit:

            if len(self.urls) > 0:
                for url in self.urls:
                    if url not in self.scraped_urls:
                        break
            soup = self.make_soup(url)
            if soup:
                mapped_books, df_book = self.extract_info_from_soup(soup)

                self.scraped_urls.add(url)
                self.books = pd.concat([self.books, df_book])
                self.book_mapping = pd.concat([self.book_mapping, mapped_books])

                counter += 1
                time.sleep(random.randint(0, 5))

                if counter % 5 == 0:
                    self.books.to_csv(self.book_file, index=False)
                    self.book_mapping.to_csv(self.book_mapping_file, index=False)
                    self.logger.info(f"Count #{counter} = {url}")

        self.books.to_csv(self.book_file, index=False)
        self.book_mapping.to_csv(self.book_mapping_file, index=False)


if __name__ == '__main__':
    bs = BookScraper()
    bs.scrape_for_books()
