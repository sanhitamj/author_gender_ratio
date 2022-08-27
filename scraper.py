from bs4 import BeautifulSoup as BSHTML
import http
import logging
import pandas as pd
import random
import time
import urllib
from urllib.request import urlopen

logging.basicConfig(level=logging.INFO, format='%(message)s')
random.seed(13)

# ToDo -
# Some Author's pages don't work. Investigate. Currently shabby solution was not_use_list
# Some lines in the output dataframes are NAs. Fix that.


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
        try:
            df_mapping = pd.read_csv(self.author_mapping_csv)
            self.mapped_authors = set(df_mapping['author'].unique())
            self.author_mapping = df_mapping.to_dict(orient='split')['data']
            self.logger.info(f'Author mapping found with {len(self.mapped_authors)} items.')
        except (pd.errors.EmptyDataError, FileNotFoundError):
            self.author_mapping = []
            self.mapped_authors = set()

        self.not_use_list = [
            # "Gabriel García Márquez",
            # "Honorée Fanonne Jeffers",
            # "Maggie O'Farrell",
            # "Haider, Tabib",
            # "Emily Brontë",
            # "RABBIT & TURTLE",
            # "Quiara Alegría Hudes",
            # "Stephen Sondheim",
            # "Elizabeth Strout",
            # "Rebecca Solnit",
            # "Rocket Classic Collection",
            # "Alice L Baumgartner",
            # "Zora Neale Hurston",
            # "Daniel Goleman",
            # "Leonard Cohen",
            # "Carol Burnett",
            # "Caitlin Rother"
        ]
        # for some reason this one would get stuck.

        self.author_data_csv = "author_data.csv"
        df_data = pd.read_csv(self.author_data_csv, na_values='NA')
        if 'Unnamed: 0' in df_data.columns:
            df_data.drop(columns=['Unnamed: 0'], inplace=True)
        if "about" in df_data.columns:
            df_data.loc[df_data["about"].isna(), "about"] = 'NA'
        df_data.loc[df_data["author_url"].isna(), "author_url"] = 'NA'
        self.author_data = df_data.set_index('author').T.to_dict()
        self.logger.info(f'Author data found with {len(self.author_data)} items.')
        self.author_url_prefix = "https://www.amazon.com/"
        self.limit = 3141  # scrape only these many number of authors' mapping.

    def get_soup(self, author="Chimamanda-Ngozi-Adichie"):

        if self.author_data[author].get("author_url", "NA") != 'NA':
            try:
                page = urlopen(self.author_url_prefix + self.author_data[author]["author_url"])
                soup = BSHTML(page, features="html.parser")
                return soup
            except (urllib.error.HTTPError, urllib.error.URLError, http.client.IncompleteRead):
                pass

    def get_authors_img_urls(self, soup, author="Chimamanda-Ngozi-Adichie"):
        rec_authors = []

        try:
            for item in soup.find_all(class_="authorListImage"):
                rec_auth = item["alt"]  # recommended author with the starting author.
                rec_authors.append(rec_auth)
                # Add a tuple of author and her correspoding authors as a list to a list of author_mapping.
                self.author_mapping.append([author, rec_auth])

                # If the recommended author isn't in the Author Data, add them.
                if rec_auth not in self.author_data:
                    self.author_data[rec_auth] = {}
                self.author_data[rec_auth]["img_url"] = (item["src"])

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
                    if rec_auth not in self.author_data:
                        self.author_data[rec_auth] = dict()
                    self.author_data[rec_auth]["author_url"] = auth_link

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

        new_authors = [
            author for author in self.author_data
            if self.author_data[author].get("author_url") != 'NA'  # we need their URL to scrape their data.
            and self.author_data[author].get("about", "NA") == 'NA'  # if we have about, we have mapping.
            and author not in self.not_use_list  # for some authors, the code is breaking.
            and author not in self.mapped_authors  # if we have their mapping, we are done here.
        ]

        counter = len(self.mapped_authors)

        while counter <= self.limit:
            author = new_authors[counter]
            self.logger.info(f'Author - {author}')
            new_authors.remove(author)

            # scrape data where author_url is known and about isn't scraped yet.
            soup = self.get_soup(author=author)
            rec_authors = self.get_authors_img_urls(soup, author=author)
            if rec_authors:
                self.get_author_urls(soup, rec_authors)
                self.scrape_about_author(soup, author=author)
                self.mapped_authors.add(author)
                new_authors += rec_authors
                time.sleep(random.randint(0, 10))
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
        df_mapping = pd.DataFrame(self.author_mapping, columns=['author', 'mapped_author'])
        self.logger.info(f"Number of Authors for whom mapping is scraped = {len(self.mapped_authors)}")
        df_mapping.to_csv(self.author_mapping_csv, na_rep='NA', index=False)


if __name__ == '__main__':
    scraper = AmazonScraper()
    scraper.scrape_amazon_site()
