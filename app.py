import streamlit as st
import psycopg2
from db import get_db_conn
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load environment variables
# os.environ.clear()
load_dotenv()



# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
print(os.getenv("OPENAI_API_KEY"))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Construct SQL query
    if section_filter:
        query = "SELECT * FROM news WHERE section = %s"
        cur.execute(query, (section_filter,))
    else:
        cur.execute("SELECT * FROM news")
    
    articles = cur.fetchall()
    conn.close()
    return articles

def generate_abstract(paragraph):
    # Construct prompt
    prompt = f"Summarize the following text with simple English and Chinese:\n{paragraph}\n\n"
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    st.title('NYT Articles')

    # Get all sections from the database
    all_sections = fetch_sections_from_db()

    # Section filter
    section_filter = st.selectbox('Select section to filter:', ['', *all_sections])

    # Get articles based on section filter
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
            st.write(f"**Paragraph:** {article[6]}")

            # Generate abstract
            if st.button(f'Generate Abstract {idx}'):
                abstract = generate_abstract(article[6])
                st.write(f"**Abstract:** {abstract}")
                st.write('---')
                
if __name__ == "__main__":
    main()
