import json

import psycopg2  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup

from news_crawler.src.scraping import BaseCrawler  # type: ignore
from news_crawler.src.utility.logger import LogHandler

logger = LogHandler()  # Đặt logger bên ngoài

class GithubTrendy(BaseCrawler):
    def __init__(self,
                 url: str = 'https://github.com/trending',
                 lang: str = 'en',
                 date: str = 'daily',
                 code_lang: str = 'python',
                 base_url = 'https://github.com',
                 timeout = 30):
        super(GithubTrendy, self).__init__()

        self.url = url
        self.lang = lang
        self.date = date
        self.code_lang = code_lang
        self.base_url = base_url
        self.timeout = timeout
        
        if self.date in ['daily', 'weekly']:
            self.trendy_filter = f"{self.url}/{self.code_lang}?since={self.date}&spoken_language_code={self.lang}"
        else:
            self.trendy_filter = self.url

        self.logger = logger  # Sử dụng logger chung

    @staticmethod
    def get_html(url):
        response = requests.get(url=url, timeout=30)
        return BeautifulSoup(response.text, "lxml")

    @staticmethod
    def save_db(data):
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
            GithubTrendy.save_db(data)  
        else:
            GithubTrendy.save_dict(data)

    def extract(self):
        soup = self.get_html(self.trendy_filter)
        repos_data = []

        for item in soup.find_all('article'):
            repo = item.h2.a['href']
            description = item.p.text.strip() if item.p else ""
            stars = item.find('span', class_='d-inline-block float-sm-right')
            stars = int(stars.text.strip().split(" ")[0].replace(',', '')) if stars else 0

            repo_data = {
                'repo': f"{self.base_url}{repo}",
                'description': description,
                'star_gain_today': stars
            }
            repos_data.append(repo_data)

        return repos_data
    
    def run(self, to_db=False):
        self.logger.info("Extracting information from Github Trending ...")
        repos_data = self.extract()
        
        GithubTrendy.save(repos_data, to_db)
        if to_db:
            self.logger.info("Information saved from Github Trending to PostgreSQL.")
        else: 
            self.logger.info("Information saved from Github Trending as a JSON file.")
