import json
import secrets
import time
from typing import Dict, List, Optional

import psycopg2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from news_crawler.src.scraping import BaseCraper  # type: ignore
from news_crawler.src.scraping.from_org.unsloth import SETTINGS  # type: ignore
from news_crawler.src.utility.logger import LogHandler

logger = LogHandler() 


class UnslotBlogPost(BaseCraper):
    def __init__(self,
                 base_url: str = "https://unsloth.ai", 
                 url: str = "https://unsloth.ai/blog",
                 config: Dict = SETTINGS):
        super(UnslotBlogPost, self).__init__()
        
        self.url = url
        self.config = config
        self.base_url = base_url
        self.logger = logger
    @staticmethod
    def chrome_cfg():
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # create headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # add user agent for simulating human action
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # disable js webdriver
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        return chrome_options 

    @staticmethod
    def _initializer(options):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options= options)
        
        # disable automation detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # driver.execute_script("window.navigator.chrome = { runtime: {},  };")
        # driver.execute_script("window.navigator.chrome.runtime = { id: 'chrome-id' };")

        return driver
    @staticmethod
    def sleep():
        sleep_time = secrets.SystemRandom().uniform(2, 8)  # Tạo số ngẫu nhiên an toàn
        logger.info(f"Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    
    
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
            UnslotBlogPost.save_db(data)  
        else:
            UnslotBlogPost.save_dict(data)
    
    @staticmethod
    def close_process(driver):
        driver.close()
        driver.quit()
    
    def get_html(self):
        driver = UnslotBlogPost._initializer(UnslotBlogPost.chrome_cfg())
        
        self.sleep()
        
        driver.get(self.url)
        if driver.execute_script("return document.readyState") == "complete":
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return soup
        
    def select_unique_blog(self,
        list_item: list, 
        redundant_tag: Optional[List]):
        """
        Unique blog thì phải là 
        - có blog tag
        - không phải nhãn thẻ about, introducing, privacy, terms, pricing
        - không bắt đầu bằng https
        """
        list_item = list(set(list_item))

        blog_items = [f"{self.base_url}/{blog}" for blog in list_item]
        blog_items = [blog_item for blog_item in blog_items if "blog" in blog_item and not any(redundant_tag in blog_item for redundant_tag in redundant_tag)] #type: ignore
        return blog_items
    
    def extract(self):
        soup = self.get_html()
        
        blogs= []
        publications = []
        for item in soup.find_all('div', class_ = self.config.get('item_class')):
            blog = item.find('a').get('href')
            publication_date = item.find('span').text.strip()

            blogs.append(blog)
            publications.append(publication_date)
        
        blogs = self.select_unique_blog(blogs, self.config.get('redundant_tag'))
    
    def run(self, to_db = False):
        self.logger.info("Extracting post link from Unsloth ...")
        article_infos = self.extract()
        
        UnslotBlogPost.save(article_infos, to_db = to_db)
        self.logger.info("Information saved from UnslotBlogPost Trending as a JSON tempt file.")
        
        #Todo:
        # From content to Unsloth Summarization Content