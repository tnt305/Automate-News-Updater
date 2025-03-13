import json
from typing import Dict, Optional

import psycopg2  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup

from news_crawler.src.scraping import BaseCraper  # type: ignore
from news_crawler.src.scraping.from_org.hf import SETTINGS
from news_crawler.src.utility.error import RequestConnectionError
from news_crawler.src.utility.logger import LogHandler
from news_crawler.src.utility.settings import Paper

logger= LogHandler()
settings = SETTINGS


class HuggingFaceNewsPaper(BaseCraper):
    def __init__(self,
                 url: str = 'https://huggingface.co/papers',
                 year: int = 2023,
                 month: int = 1,
                 day: int = 1,
                 timeout: int = 30,
                 retries: int = 5,
                 redundant_item: Optional[Dict | None] = settings):
        super(HuggingFaceNewsPaper, self).__init__()
        
        self.url = url
        self.year = year
        self.month = month
        self.day = day
        self.timeout = timeout
        self.retries = retries
        self.sesion = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries = self.retries)
        self.session.mount("https//", adapter)

        self.redundant_item = redundant_item
        
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
            HuggingFaceNewsPaper.save_db(data)  
        else:
            HuggingFaceNewsPaper.save_dict(data)
            
            
    def extract(self):
        soup = self.get_html(self.url)
        
        article_infos= []
        
        for item in soup.find_all('article'):
            # Lấy tên paper
            paper_name = item.find('h3').text
            # lấy link paper 
            paper_id = item.find('a').get('href').split("/")[-1]
            # Đếm số lượng upvote
            divs = item.select('div.leading-none')
            for div in divs:
                if div.get("class") == ["leading-none"]:
                    paper_upvote = int(div.text)
                else:
                    paper_upvote = 0
            
            detail = requests.get(f"{self.url}/{paper_id}", timeout = self.timeout)
            
            if detail.status_code == 200:
                soup_detail  = BeautifulSoup(detail.text, 'lxml')
                
                tags = soup_detail.find_all('a', class_ = "cursor-pointer")
                keywords = list(set([tag.text for tag in tags if not any(headkeyword in tag.text for headkeyword in self.redundant.get("to_remove"))]))
                
                abstract = []
                for item in tags:
                    subabstract = item.text.strip().replace("\n", "")
                    if not any(headkeyword in subabstract for headkeyword in self.redundant.get("to_remove")):
                        abstract.append(subabstract)
                    else:
                        continue
                abstract = " ".join(abstract)
            else:
                continue

            article_infos.append(Paper(paper_name, paper_id, paper_upvote, keywords, abstract))
        return article_infos
    
    def run(self, to_db =False):
        self.logger.info("Extracting information from HuggingFaceNewsPaper ...")
        article_infos = self.extract()
        
        HuggingFaceNewsPaper.save(article_infos, to_db)
        if to_db:
            self.logger.info("Information saved from HuggingFaceNewsPaper Trending to PostgreSQL.")
        else: 
            self.logger.info("Information saved from HuggingFaceNewsPaper Trending as a JSON file.")
        
    
                