from bs4 import BeautifulSoup as BSHTML
import pandas as pd
from urllib.request import urlopen


class AmazonScraper:
    """
    Starts with one author name, and her  Amazon page. From there the scraper should pick
    more author names, their URLs. This code will store -
        1. Author Name
        2. About the Author.
        3. Author's Amazon img_url
        4. All the authors (12) that are associated with this Author.
        5. Their Amazon URL.
        6. Visit the URLs from #5 and gather 1-5 for them.
        7. Until it has found self.limit number of distinct Authors.
    """

    def __init__(self):
        self.df = pd.DataFrame()
        self.author_mapping = {}
        self.author_data = {
            "Chimamanda-Ngozi-Adichie": {
                "author_url": "Chimamanda-Ngozi-Adichie/e/B00PODW5UG",
                "img_url":
                    "https://m.media-amazon.com/images/S/amzn-author-media-prod/fbj91cmerepo1mce3chcvrpqqc._SX450_.jpg",
            },
            # 'Elise Bohan': "https://www.amazon.com/Elise-Bohan/e/B09X6CPCYR"
        }
        self.author_url_prefix = "https://www.amazon.com/"
        self.limit = 3141  # scrape only these many number of authors.

    def get_soup(self, author="Chimamanda-Ngozi-Adichie"):

        page = urlopen(self.author_url_prefix + self.author_data[author]["author_url"])
        soup = BSHTML(page)
        return soup

    def get_authors_img_urls(self, soup, author="Chimamanda-Ngozi-Adichie"):
        self.author_mapping[author] = []

        rec_authors = []
        for item in soup.find_all(class_="authorListImage"):
            rec_auth = item["alt"]
            rec_authors.append(rec_auth)

            self.author_mapping[author].append(rec_authors)
            self.author_data[rec_auth]["img_url"] = (item["src"])
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

        for author in self.author_urls:
            soup = self.get_soup(author=author)
            rec_authors = self.get_authors_img_urls(soup, author)
            self.get_author_urls(soup, author, rec_authors)

    def scrape_about_author(self, soup, author="Chimamanda-Ngozi-Adichie"):
        """
        About the author section is important; it may use pronounce like She/Her
        or He/Him to identify the gender.
        """
        about = []
        for item in soup.find('span', {'id': 'author_biography'}):
            about.append(item.text.strip())

        about = [item for item in about if item]
        self.author_data[author]["about"] = about[0]

    def write_dataframe(self):
        for author in self.author_urls:
            # write a small dataframe, append it to the bigger one.
            # This is inefficient. But I am a Data Scientist! ;-)
            pass


if __name__ == '__main__':
    pass
