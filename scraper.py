from bs4 import BeautifulSoup as BSHTML
import logging
import pandas as pd
import time
import urllib
from urllib.request import urlopen

logging.basicConfig(level=logging.INFO, format='%(message)s')

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

        self.logger = logging.getLogger(__name__)
        self.author_mapping_csv = "author_mapping.csv"
        df_mapping = pd.read_csv(self.author_mapping_csv)
        self.author_mapping = df_mapping.set_index('Unnamed: 0').T.to_dict(orient='list')
        self.logger.info(f'Author mapping found with {len(self.author_mapping)} items.')

        self.author_data_csv = "author_data.csv"
        df_data = pd.read_csv(self.author_data_csv)
        if 'Unnamed: 0' in df_data.columns:
            df_data.drop(columns=['Unnamed: 0'], inplace=True)
        df_data.loc[df_data["about"].isna(), "about"] = 'NA'
        df_data.loc[df_data["author_url"].isna(), "author_url"] = 'NA'
        self.author_data = df_data.set_index('author').T.to_dict()
        self.logger.info(f'Author data found with {len(self.author_data)} items.')

        # for non-fiction
        # "Elise Bohan": {
        #     "author_url": "Elise-Bohan/e/B09X6CPCYR",
        #     "img_url": "",
        # }

        self.author_url_prefix = "https://www.amazon.com/"
        self.limit = 3141  # scrape only these many number of authors.

    def get_soup(self, author="Chimamanda-Ngozi-Adichie"):

        if self.author_data[author]["author_url"] != 'NA':
            page = urlopen(self.author_url_prefix + self.author_data[author]["author_url"])
            try:
                soup = BSHTML(page, features="html.parser")
                return soup
            except urllib.error.HTTPError:
                pass

    def get_authors_img_urls(self, soup, author="Chimamanda-Ngozi-Adichie"):
        self.author_mapping[author] = []
        author_data = {}
        rec_authors = []

        try:
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
        except AttributeError:
            pass

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
            if rec_authors:
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

    def scrape_amazon_site(self):

        new_authors = [author for author in self.author_data
                       if self.author_data[author].get("author_url") and self.author_data[author]["about"] == 'NA']
        len_existing_data = len(new_authors)
        counter = 0
        self.logger.info(f'Number of new authors = {len(new_authors)}')

        # while counter + len_existing_data <= self.limit:
        while counter + len_existing_data <= 100:
            author = new_authors[counter]

            # scrape data where author_url is known and about isn't found yet.
            if self.author_data[author].get("author_url") and self.author_data[author]["about"] == 'NA':
                soup = self.get_soup(author=author)
                rec_authors = self.get_authors_img_urls(soup, author=author)
                if rec_authors:
                    self.logger.info(f'Author - {author}')
                    self.get_author_urls(soup, rec_authors)
                    self.scrape_about_author(soup, author=author)
                    new_authors.remove(author)
                    new_authors += rec_authors
                    time.sleep(3)
                    counter += 1
                    if counter % 5 == 0:
                        self.write_dataframes()

    def write_dataframes(self):
        df_data = pd.DataFrame.from_dict(self.author_data).T.reset_index().rename(columns={'index': 'author'})
        if 'Unnamed: 0' in df_data.columns:
            df_data.columns.drop(columns='Unnamed: 0', inplace=True)
        self.logger.info(f"Scraped Author info dataframe shape = {df_data.shape}")
        df_data.to_csv(self.author_data_csv, na_rep='NA', index=False)

        # the following dataframe should have only 2 columns ideally. But let us worry about it later.
        df_mapping = pd.DataFrame.from_dict(self.author_mapping, orient="index")
        self.logger.info(f"Scraped author mapping dataframe shape = {df_mapping.shape}")
        df_mapping.to_csv(self.author_mapping_csv, na_rep='NA', index=False)


if __name__ == '__main__':
    scraper = AmazonScraper()
    scraper.scrape_amazon_site()
