# MyApp README

## Introduction
My app is designed to fetch and display articles from the New York Times (NYT) API. It extracts relevant information from the articles such as title, URL, published date, author, and section, and stores this information in a JSON file named "links.json". Additionally, it extracts paragraphs from the articles and includes them in the stored information.

check it out here!: https://axi-techin510-final.azurewebsites.net/

## Problems Addressed
- Easy access to the latest articles from the New York Times (NYT) 
- Providing summarized content for efficient consumption with chinese and english


## Code Explanation
The code consists of three parts:

### Part 1: NYT API Data Fetching (data.py+ db.py)
- This Python script fetches the latest articles from the New York Times API.
- It utilizes libraries such as requests, dotenv, json, time, and BeautifulSoup for data retrieval and parsing.
- The main function `fetch_latest_articles(source, section)` retrieves articles from the NYT API based on the specified source and section.
- It then extracts relevant information from the API response, including titles, URLs, published dates, authors, and sections.
- Paragraphs are extracted from each article's URL using the `extract_paragraphs(url)` function.
- Finally, the extracted information is stored in a JSON file named "links.json".

### Part 2: Streamlit Web Application (app.py)
- This part of the code creates a web application using Streamlit to display articles fetched from a database.
- It imports necessary libraries such as Streamlit and psycopg2 for database connectivity.
- The `fetch_articles_from_db()` function retrieves articles from the database.
- It then displays the fetched articles on the web interface, showing details such as title, published date, author, section, source, URL, and paragraph.

### Part 3: OpenAI Integration (app.py)
- This part of the code integrates with OpenAI to generate summaries for article paragraphs.
- It imports the OpenAI library and dotenv for environment variable loading.
- The `generate_abstract(paragraph)` function utilizes OpenAI's API to generate a summary for a given paragraph of text.
- In the main function, summaries are generated for each article paragraph fetched from the database, and displayed along with other article details.

## How to run the code
To use the app:
1. Ensure you have the necessary environment variables set up, such as API keys for NYT and OpenAI, and database connection details.
2. Run the respective Python scripts for each part of the application.
3. Access the web interface generated by Streamlit to view the articles fetched from the database, filtered by section if desired.

Feel free to explore and modify the code to suit your needs!

## Reflections
- **What I Learned:**
  - Efficient data retrieval and parsing techniques
  - Integration of external APIs into web applications
  - Database connectivity and management
  - More convenient operations using APIs
  - Using headers in BeautifulSoup requests

- **Challenges Faced:**
  - Ensuring secure handling of API keys and environment variables
  - Optimizing the summarization process for better performance
  - Handling asynchronous tasks efficiently
  - Ensuring scalability of the application
  - Overcoming the issue of excessive API requests to OpenAI by implementing a button to generate abstracts only upon user request

## License
This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
