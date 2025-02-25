from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import json
import logging
import os
import requests

# 设置更详细的日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

class TwitterNewsScraper:
    def __init__(self):
        try:
            logging.info("Initializing Chrome options...")
            self.options = webdriver.ChromeOptions()
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--no-sandbox')
            self.options.add_argument('--disable-dev-shm-usage')
            
            logging.info("Setting up ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.wait = WebDriverWait(self.driver, 20)
            logging.info("Browser initialized successfully")
            
            # 打印当前工作目录
            logging.info(f"Current working directory: {os.getcwd()}")
        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            raise

    def get_tech_news(self):
        try:
            logging.info("Accessing Twitter news page...")
            self.driver.get('https://twitter.com/explore/tabs/news')
            logging.info("Waiting for page load...")
            time.sleep(10)  # 增加等待时间

            # 获取页面标题和URL，用于调试
            logging.info(f"Current page title: {self.driver.title}")
            logging.info(f"Current URL: {self.driver.current_url}")

            # 尝试获取页面内容
            logging.info("Trying to find news items...")
            news_items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
            )
            logging.info(f"Found {len(news_items)} news items")

            tech_news = []
            for i, item in enumerate(news_items[:5]):  # 只处理前5条用于测试
                try:
                    tweet_text = item.text
                    logging.info(f"Tweet {i+1} content: {tweet_text[:100]}...")  # 只记录前100个字符
                    tech_news.append({
                        'text': tweet_text,
                        'scraped_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    logging.error(f"Error processing tweet {i+1}: {str(e)}")

            return tech_news

        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            self.driver.quit()

    def save_to_file(self, news_list):
        try:
            filename = f"tech_news_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = os.path.join(os.getcwd(), filename)
            logging.info(f"Saving to file: {filepath}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=4)
            logging.info("File saved successfully")
        except Exception as e:
            logging.error(f"Error saving to file: {str(e)}")

def main():
    try:
        logging.info("Starting the scraper...")
        scraper = TwitterNewsScraper()
        tech_news = scraper.get_tech_news()
        
        if tech_news:
            logging.info(f"Found {len(tech_news)} news items")
            scraper.save_to_file(tech_news)
        else:
            logging.warning("No news items found")
            
    except Exception as e:
        logging.error(f"Main function error: {str(e)}")

if __name__ == "__main__":
    main()

try:
    # 你的请求代码
    logging.info("Attempting to connect to Twitter...")
    response = requests.get(url, headers=headers, timeout=10)
    logging.info("Connection successful!")
except Exception as e:
    logging.error(f"An error occurred: {e}") 