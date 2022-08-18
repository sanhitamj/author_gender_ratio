from bs4 import BeautifulSoup as BSHTML
import pandas as pd
from urllib.request import urlopen




author_urls

# Get the HTML source



class AmazonScraper:


    def __init__(self):
        self.df = pd.DataFrame()
        self.data_dict = {}
        self.author_urls = {
            'Chimamanda-Ngozi-Adichie': "Chimamanda-Ngozi-Adichie/e/B00PODW5UG",
            # 'Elise Bohan': "https://www.amazon.com/Elise-Bohan/e/B09X6CPCYR"
        }
        self.author_url_prefix = 'https://www.amazon.com/'
        self.limit = 3141
        # scrape only these many number of authors.

    def get_soup(self, author='Chimamanda-Ngozi-Adichie'):

        page = urlopen(self.author_url_prefix + self.author_urls[author])
        soup = BSHTML(page)
        return soup

    def get_authors_img_urls(self, soup, author):
        self.data_dict[author] = {}

        rec_authors = []
        auth_img = []
        for item in soup.find_all(class_="authorListImage"):
            rec_auth = item["alt"]
            rec_authors.append(rec_auth)

            self.data_dict[author][rec_auth] = []
            self.data_dict[author][rec_auth].append(item["src"])

        return rec_authors


    def get_author_urls(self, soup, author, rec_authors):
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
                    self.data_dict[author][rec_auth].append(auth_link)
                    if rec_auth not in self.author_urls and len(author_urls) < self.limit:
                        self.author_urls[rec_auth] = auth_link


        def scrape_authors(self):

            for author in self.author_urls:
                soup = self.get_soup(author=author)
                rec_authors = self.get_authors_img_urls(soup, author)
                self.get_author_urls(soup, author, rec_authors)

        def write_dataframe(self):
            for author in self.author_urls:
            # write a small dataframe, append it to the bigger one.
            # This is inefficient. But I am a Data Scientist! ;-)
                pass
