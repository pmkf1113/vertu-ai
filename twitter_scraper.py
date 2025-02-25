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
import requests
import os
import tempfile

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='twitter_scraper.log'
)

class TwitterNewsScraper:
    def __init__(self):
        try:
            # 强制关闭所有Chrome实例
            os.system("pkill -f Chrome")
            
            # 初始化Chrome选项
            self.options = webdriver.ChromeOptions()
            
            # 其他必要的配置
            self.options.add_argument('--no-sandbox')
            self.options.add_argument('--disable-dev-shm-usage')
            self.options.add_argument('--start-maximized')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--remote-debugging-port=9222')
            self.options.add_argument('--disable-extensions')
            self.options.add_argument('--disable-software-rasterizer')
            
            # 使用 webdriver_manager 自动管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            
            self.wait = WebDriverWait(self.driver, 20)
            logging.info("Browser initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            raise

    def get_tech_news(self):
        try:
            logging.info("Starting news collection...")
            search_url = 'https://www.buzzing.cc/'
            self.driver.get(search_url)
            logging.info(f"Accessing URL: {search_url}")
            
            # 等待页面加载
            time.sleep(10)
            
            # 获取科技新闻
            tech_news_list = self._get_section_news('tech')
            
            # 获取国外新闻头条
            foreign_news_list = self._get_foreign_news()
            
            return {
                'top_news': tech_news_list,
                'foreign_news': foreign_news_list
            }
            
        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            return {}
        finally:
            self.driver.quit()

    def _get_section_news(self, section_name):
        """获取指定板块的新闻"""
        try:
            # 增加等待时间，确保页面完全加载
            time.sleep(5)
            
            # 找到所有文章卡片
            articles = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.article.h-entry.hentry.card"))
            )
            
            news_list = []
            for i, article in enumerate(articles[:10]):  # 只取前10篇文章
                try:
                    # 获取标题和链接
                    title_element = article.find_element(By.CSS_SELECTOR, "a.p-name.entry-title")
                    title = title_element.text.strip()
                    if title.startswith(str(i+1) + ". "):  # 去掉序号
                        title = title[len(str(i+1) + ". "):]
                    url = title_element.get_attribute('href')
                    
                    # 获取HN分数
                    points_element = article.find_element(By.CSS_SELECTOR, "a.no-underline.muted.small")
                    points = points_element.text.strip()  # 格式如 "↑ 100 HN Points"
                    
                    # 获取时间
                    time_element = article.find_element(By.CSS_SELECTOR, "time.dt-published")
                    post_time = time_element.text.strip()
                    
                    logging.info(f"Found article {i+1}: {title[:100]}...")
                    
                    news_list.append({
                        'rank': i + 1,
                        'title': title,
                        'url': url,
                        'points': points,
                        'time': post_time,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logging.error(f"Error processing article {i+1}: {str(e)}")
                    continue
            
            return news_list
            
        except Exception as e:
            logging.error(f"Error getting articles: {str(e)}")
            return []

    def _get_foreign_news(self):
        """获取国外新闻头条"""
        try:
            # 等待页面加载
            time.sleep(5)
            
            # 找到国外新闻头条板块
            news_section = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "details#news"))
            )
            
            # 确保板块展开
            if not news_section.get_attribute("open"):
                summary = news_section.find_element(By.TAG_NAME, "summary")
                summary.click()
                time.sleep(2)
            
            # 找到所有文章卡片
            articles = news_section.find_elements(By.CSS_SELECTOR, "div.article.h-entry.hentry.card")
            
            news_list = []
            for i, article in enumerate(articles[:10]):  # 只取前10篇文章
                try:
                    # 获取标题和链接
                    title_element = article.find_element(By.CSS_SELECTOR, "a.p-name.entry-title")
                    title = title_element.text.strip()
                    if title.startswith(str(i+1) + ". "):  # 去掉序号
                        title = title[len(str(i+1) + ". "):]
                    url = title_element.get_attribute('href')
                    
                    # 获取摘要
                    summary_element = article.find_element(By.CSS_SELECTOR, "div.p-summary.entry-summary")
                    summary = summary_element.text.strip()
                    
                    # 获取时间和标签
                    footer = article.find_element(By.CSS_SELECTOR, "footer")
                    time_element = footer.find_element(By.CSS_SELECTOR, "time")
                    post_time = time_element.text.strip()
                    
                    # 尝试获取标签（如果存在）
                    tags = []
                    try:
                        tag_elements = footer.find_elements(By.CSS_SELECTOR, "a[href*='/tags/']")
                        tags = [tag.text.strip('#') for tag in tag_elements]
                    except:
                        pass
                    
                    logging.info(f"Found foreign news {i+1}: {title[:100]}...")
                    
                    news_list.append({
                        'rank': i + 1,
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'time': post_time,
                        'tags': tags,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logging.error(f"Error processing foreign news article {i+1}: {str(e)}")
                    continue
            
            return news_list
            
        except Exception as e:
            logging.error(f"Error getting foreign news: {str(e)}")
            return []

    def save_to_file(self, news_list):
        """将结果保存到JSON文件"""
        try:
            filename = f"tech_news_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully saved news to {filename}")
        except Exception as e:
            logging.error(f"Error saving to file: {str(e)}")

    def send_to_api(self, news_data):
        """将新闻数据发送到第三方接口"""
        try:
            api_url = "https://table.vertu.cn/fusion/v1/datasheets/dsthwwvl9zpWwQV1ul/records"
            headers = {
                "Authorization": "Bearer usknceqWtY2RUae0JtfwVOY",
                "Content-Type": "application/json"
            }
            
            # 准备请求数据
            records = []
            
            # 处理科技新闻
            for news in news_data.get('top_news', []):
                records.append({
                    "fields": {
                        "热门新闻": news['title'],
                        "日期": int(datetime.now().timestamp() * 1000)  # 转换为毫秒时间戳
                    }
                })
                
            # 处理国外新闻
            for news in news_data.get('foreign_news', []):
                records.append({
                    "fields": {
                        "热门新闻": news['title'],
                        "日期": int(datetime.now().timestamp() * 1000)
                    }
                })
            
            # 构建请求数据
            payload = {
                "records": records,
                "fieldKey": "name"
            }
            
            # 发送请求
            response = requests.post(
                f"{api_url}?viewId=viw2yvqffCKwH&fieldKey=name",
                headers=headers,
                json=payload
            )
            
            # 检查响应
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logging.info("Successfully sent data to API")
                    return True
                else:
                    logging.error(f"API error: {result.get('message')}")
                    return False
            else:
                logging.error(f"API request failed with status code: {response.status_code}")
                return False
            
        except Exception as e:
            logging.error(f"Error sending data to API: {str(e)}")
            return False

def main():
    try:
        scraper = TwitterNewsScraper()
        news_data = scraper.get_tech_news()
        
        if news_data:
            # 保存数据到文件
            scraper.save_to_file(news_data)
            
            # 发送数据到API
            if scraper.send_to_api(news_data):
                print("Successfully sent data to API")
            else:
                print("Failed to send data to API")
            
            # 打印科技新闻结果
            print("\n科技新闻:")
            for news in news_data['top_news']:
                print(f"{news['rank']}. {news['title'][:100]}...")
                
            # 打印国外新闻头条结果
            print("\n国外新闻头条:")
            for news in news_data['foreign_news']:
                print(f"{news['rank']}. {news['title'][:100]}...")
        else:
            print("No news found")
    except Exception as e:
        logging.error(f"Main function error: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
