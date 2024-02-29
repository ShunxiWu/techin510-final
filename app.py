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
    
    # Convert each tuple to a dictionary for easier access
    keys = ['url', 'title', 'published_date', 'byline', 'section', 'source', 'paragraph', 'image_url']
    articles = [dict(zip(keys, article)) for article in articles]
    
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

    for idx, article in enumerate(articles):
                # Check if 'image_url' key exists

        st.markdown(f"<h1>{article['title']}</h1>", unsafe_allow_html=True)
        if 'image_url' in article:
            # Try to display the image, catch exceptions if the format is not supported
            try:
                st.image(article['image_url'], caption='Article Image', use_column_width=True)
            except Exception as e:
                st.write(f"Failed to display image for article {idx+1}: {e}")
        else:
            st.write("Image not available.")  
        st.write(f"**Published Date:** {article['published_date']}")
        st.write(f"**Byline:** {article['byline']}")
        st.write(f"**Section:** {article['section']}")
        st.write(f"**Source:** {article['source']}")
        st.write(f"**URL:** [{article['title']}]({article['url']})")

        # Check if 'paragraph' key exists
        if 'paragraph' in article:
            # st.write(f"**Paragraph:** {article['paragraph']}")
            button_label = f"Generate Abstract {idx}"  # Unique identifier
            if st.button(button_label):
                abstract = generate_abstract(article['paragraph'])
                st.write(f"**Abstract:** {abstract}")
        else:
            st.write("Paragraph data not available.")

        st.write('---')

if __name__ == "__main__":
    main()
