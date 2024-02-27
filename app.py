import streamlit as st
import psycopg2
from db import get_db_conn
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 设置 OpenAI API
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
print(os.getenv("OPENAI_API_KEY"),
    os.getenv("OPENAI_API_BASE"))

def fetch_sections_from_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT section FROM news")
    sections = cur.fetchall()
    conn.close()
    return {section[0] for section in sections}

def fetch_articles_from_db(section_filter=None):
    conn = get_db_conn()
    cur = conn.cursor()

    # 构建SQL查询
    if section_filter:
        query = "SELECT * FROM news WHERE section = %s"
        cur.execute(query, (section_filter,))
    else:
        cur.execute("SELECT * FROM news")
    
    articles = cur.fetchall()
    conn.close()
    return articles

def generate_abstract(paragraph):
    # 调用 ChatGPT 生成摘要
    response = client.chat.completions.create(
        model="text-davinci-003",
        messages=[{"role": "system", "content": "Summarize the following text with simple english and chinese:"}, {"role": "user", "content": paragraph}],
        stream=False,
    )
    return response.choices[0].text.strip()

def main():
    st.title('NYT Articles')

    # 从数据库中获取所有部分名称
    all_sections = fetch_sections_from_db()

    # 部分过滤器
    section_filter = st.selectbox('Select section to filter:', ['', *all_sections])

    # 根据过滤部分获取文章
    articles = fetch_articles_from_db(section_filter)

    if not articles:
        st.write('No articles found.')
    else:
        st.write(f'Number of articles: {len(articles)}')

        for article in articles:
            st.markdown(f"**Title:** {article[1]}")
            st.write(f"**Published Date:** {article[2]}")
            st.write(f"**Byline:** {article[3]}")
            st.write(f"**Section:** {article[4]}")
            st.write(f"**Source:** {article[5]}")
            st.write(f"**URL:** [{article[1]}]({article[0]})")
            # st.write(f"**Paragraph:** {article[6]}")

            # 生成摘要
            abstract = generate_abstract(article[6])
            st.write(f"**Abstract:** {abstract}")
            time.sleep(10)
            st.write('---')

if __name__ == "__main__":
    main()
