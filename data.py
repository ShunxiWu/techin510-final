import os
import requests
from dotenv import load_dotenv
import json
import time
from bs4 import BeautifulSoup
import psycopg2

load_dotenv()

# 设置文件路径和请求标头
URL_DETAIL_FILE = './data/links.json'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_db_conn():
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS news;')
    conn.commit()
    cur.close()

    # 创建表
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS news (
            url TEXT PRIMARY KEY,
            title TEXT,
            published_date TIMESTAMP WITH TIME ZONE,
            byline TEXT,
            section TEXT,
            source TEXT,
            paragraphs TEXT[],
            image_url TEXT
        )
    ''')
    conn.commit()
    cur.close()
    
    return conn

def fetch_latest_articles(source, section):
    api_key = os.getenv("NYT_KEY")
    if api_key is None:
        raise ValueError("API_KEY is not set in the .env file")

    conn = get_db_conn()
    cur = conn.cursor()

    url = f"https://api.nytimes.com/svc/news/v3/content/{source}/{section}.json?api-key={api_key}"
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        articles = data.get('results', [])
        all_articles = []  # 存储所有文章数据
        for article in articles:
            article_info = {
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'published_date': article.get('published_date', ''),
                'byline': article.get('byline', ''),
                'section': article.get('section', ''),
                'source': article.get('source', ''),
            }
            paragraphs = extract_paragraphs(article_info['url'])
            article_info['paragraphs'] = paragraphs

            # 提取图片URL
            image_url = extract_image_url(article_info['url'])
            article_info['image_url'] = image_url

            all_articles.append(article_info)  # 将文章信息添加到列表中

            # 将文章信息插入数据库
            insert_article_to_db(cur, article_info)

        conn.commit()
        conn.close()

        # 将所有文章信息写入 JSON 文件
        with open(URL_DETAIL_FILE, "w", encoding="utf-8") as json_file:
            json.dump(all_articles, json_file, ensure_ascii=False, indent=4)
        print("All data successfully saved to JSON file:", URL_DETAIL_FILE)
    else:
        print("API call failed, status code:", response.status_code)

def extract_paragraphs(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.select("#story > section > div > div > p")
        paragraph_texts = [p.get_text() for p in paragraphs]
        return paragraph_texts
    else:
        print("Failed to fetch URL:", url)
        return []

def extract_image_url(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tags = soup.select("img.css-rq4mmj")
        if img_tags:
            return img_tags[0]['src']  # 获取第一个图片标签的 src 属性值
    else:
        print("Failed to fetch URL:", url)
        return None

def insert_article_to_db(cur, article_info):
    q = '''
    INSERT INTO news (url, title, published_date, byline, section, source, paragraphs, image_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
    '''
    cur.execute(q, (article_info['url'], article_info['title'], article_info['published_date'], article_info['byline'], article_info['section'], article_info['source'], article_info['paragraphs'], article_info['image_url']))

def main():
    source = 'all'
    section = 'all'
    fetch_latest_articles(source, section)

if __name__ == "__main__":
    main()
