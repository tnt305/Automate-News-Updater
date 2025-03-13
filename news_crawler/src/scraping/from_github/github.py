import json

import psycopg2  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup

from news_crawler.src.scraping import BaseCraper  # type: ignore
from news_crawler.src.utility.error import (FrequencyMismatchError,
                                            RequestConnectionError)
from news_crawler.src.utility.logger import LogHandler
from news_crawler.src.utility.settings import GithubTrend

logger = LogHandler() 


# https://huggingface-paper-explorer.vercel.app/
class GithubTrending(BaseCraper):
    def __init__(self,
                 url: str = 'https://github.com/trending',
                 lang: str = 'en',
                 date: str = 'daily',
                 code_lang: str = 'python',
                 base_url = 'https://github.com',
                 timeout = 30):
        super(GithubTrending, self).__init__()

        self.url = url
        self.lang = lang
        self.date = date
        self.code_lang = code_lang
        self.base_url = base_url
        self.timeout = timeout
        
        self.logger = logger
        # validation for datetime freq
        if self.date in ['daily', 'weekly']:
            self.trendy_filter = f"{self.url}/{self.code_lang}?since={self.date}&spoken_language_code={self.lang}"
        elif self.date == 'monthly':
            self.trendy_filter = self.url
        else:
            print(FrequencyMismatchError(error_root=self.date))
            self.logger.debug('Papers daily collecting start ...')
            self.trendy_filter = f"{self.url}/{self.code_lang}?since=daily&spoken_language_code={self.lang}"

            
        self.timeout = timeout 
    @staticmethod
    def get_html(url: str, timeout: int):
        with requests.Session() as session:
            try:
                response = session.get(url=url, timeout=timeout)
                response.raise_for_status()
                return BeautifulSoup(response.text, "lxml")
            except requests.RequestException as e:
                print(RequestConnectionError(url, e))

    @classmethod
    def save_db(cls, data):
        conn = psycopg2.connect(
                dbname="your_db",
                user="your_user",
                password="your_password",
                host="localhost",
                port="5432"
            )
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS repositories (
                    repo TEXT, 
                    description TEXT, 
                    star_gain_today INTEGER)''')
        for entry in data:
            cursor.execute("INSERT INTO repositories VALUES (%s, %s, %s)", 
                    (entry["repo"], entry["description"], entry["star_gain_today"]))
        
        conn.commit()
        conn.close()

    @staticmethod
    def save_dict(data):
        with open('repositories.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def save(data, to_db=False):
        if to_db:
            GithubTrending.save_db(data)  
        else:
            GithubTrending.save_dict(data)

    def extract(self):
        soup = self.get_html(self.trendy_filter, self.timeout)
        repos_data = []

        for item in soup.find_all('article'):
            repo = item.h2.a['href']
            repo = f"{self.base_url}{repo}"
            description = item.p.text.strip() if item.p else ""
            stars = item.find('span', class_='d-inline-block float-sm-right')
            stars = int(stars.text.strip().split(" ")[0].replace(',', '')) if stars else 0

            repos_data.append(GithubTrend(repo, description, stars))

        return repos_data
    
    def run(self, to_db=False):
        self.logger.info("Extracting information from Github Trending ...")
        repos_data = self.extract()
        
        GithubTrending.save(repos_data, to_db)
        if to_db:
            self.logger.info("Information saved from Github Trending to PostgreSQL.")
        else: 
            self.logger.info("Information saved from Github Trending as a JSON file.")

