from bs4 import BeautifulSoup as BSHTML
import logging
import pandas as pd
import time
from urllib.request import urlopen


class AmazonScraper:
    """
    Starts with one author name, and her  Amazon page. From there the scraper should pick
    more author names, their URLs. This code will store -
        1. Author Name
        2. About the Author.
        3. Author's Amazon img_url
        4. All the authors (12) that are associated with this Author.
        5. Their Amazon URL
        6. Visit the URLs from #5 and gather 1-5 for them.
        7. Until it has found self.limit number of distinct Authors.
    """

    def __init__(self):
        self.author_mapping = {}
        self.author_data = {
            # for fiction
            "Chimamanda-Ngozi-Adichie": {
                "author_url": "Chimamanda-Ngozi-Adichie/e/B00PODW5UG",
                "img_url":
                    "https://m.media-amazon.com/images/S/amzn-author-media-prod/fbj91cmerepo1mce3chcvrpqqc._SX450_.jpg",
            },
            # for non-fiction
            # "Elise Bohan": {
            #     "author_url": "Elise-Bohan/e/B09X6CPCYR",
            #     "img_url": "",
            # }
        }
        self.author_url_prefix = "https://www.amazon.com/"
        self.limit = 3141  # scrape only these many number of authors.
        self.output_author_data = "author_data.csv"
        self.output_author_mapping = "author_mapping.csv"
        self.logger = logging.getLogger(__name__)

    def get_soup(self, author="Chimamanda-Ngozi-Adichie"):

        try:
            page = urlopen(self.author_url_prefix + self.author_data[author]["author_url"])
            soup = BSHTML(page, features="html.parser")
            return soup
        except urllib.error.HTTPError:
            pass

    def get_authors_img_urls(self, soup, author="Chimamanda-Ngozi-Adichie"):
        self.author_mapping[author] = []
        author_data = {}

        rec_authors = []
        for item in soup.find_all(class_="authorListImage"):
            rec_auth = item["alt"]
            rec_authors.append(rec_auth)

            if rec_auth not in author_data:
                author_data[rec_auth] = {}
            author_data[rec_auth]["img_url"] = (item["src"])

        # Attach the list of recommended authors to the dictionary key of the Author.
        new_authors = [author_ for author_ in author_data if author_ not in self.author_data]
        for new_author in new_authors:
            self.author_data[new_author] = author_data[new_author]

        self.author_mapping[author] = rec_authors
        return rec_authors

    def get_author_urls(self, soup, rec_authors):
        auth_links = []
        auth_link_names = {}

        for auth in rec_authors:
            auth_link_names[auth] = ("-".join(n.strip().replace('.', '') for n in auth.split()))

        for item in soup.findAll(class_="a-link-normal"):
            if '/e/' in item["href"]:
                link = item["href"]
                idx = link.find('?ref=')
                if idx > 0:
                    link = link[:idx]
                auth_links.append(link)

        auth_links = list(set(auth_links))

        for rec_auth, link in auth_link_names.items():
            for auth_link in auth_links:
                if link in auth_link:
                    self.author_data[rec_auth]["author_url"] = auth_link

    def scrape_authors(self):

        for author in self.author_data:
            soup = self.get_soup(author=author)
            rec_authors = self.get_authors_img_urls(soup, author)
            self.get_author_urls(soup, rec_authors)

    def scrape_about_author(self, soup, author="Chimamanda-Ngozi-Adichie"):
        """
        About the author section is important; it may use pronounce like She/Her
        or He/Him to identify the gender.
        """
        about = []
        try:
            for item in soup.find('span', {'id': 'author_biography'}):
                about.append(item.text.strip())
            about = [item for item in about if item]
            self.author_data[author]["about"] = about[0]

        except TypeError:
            self.author_data[author]["about"] = "None"
            # fill this in with some string so that the scraper won't visit this page again.

    def write_dataframes(self):
        counter = 0

        new_authors = [author for author in self.author_data]
        # the first author is already in the dictionary.

        while counter <= self.limit:
            author = new_authors[counter]

            # scrape data where author_url is known and about isn't found yet.
            if self.author_data[author].get("author_url") and not self.author_data[author].get("about"):
                soup = self.get_soup(author=author)
                rec_authors = self.get_authors_img_urls(soup, author=author)
                self.get_author_urls(soup, rec_authors)
                self.scrape_about_author(soup, author=author)
                new_authors.remove(author)
                new_authors += rec_authors
                time.sleep(3)
                counter += 1

        df_data = pd.DataFrame.from_dict(self.author_data).T.reset_index().rename(columns={'index': 'author'})
        self.logger.info(f"Scraped Author info dataframe shape = {df_data.shape}")
        df_data.to_csv(self.output_author_data)

        # the following dataframe should have only 2 columns ideally. But let us worry about it later.
        df_mapping = pd.DataFrame.from_dict(self.author_mapping, orient="index")
        self.logger.info(f"Scraped author mapping dataframe shape = {df_mapping.shape}")
        df_mapping.to_csv(self.output_author_mapping)


if __name__ == '__main__':
    scraper = AmazonScraper()
    scraper.write_dataframes()
