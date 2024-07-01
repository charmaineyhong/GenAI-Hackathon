import pandas as pd
import sqlite3
import streamlit as st

#title of page
st.title("Database")

# Connect to the database
sqlite_connection = sqlite3.connect("news_database.db")
c = sqlite_connection.cursor()

# User input for search criteria
search_field = st.selectbox("Select search field:", ["URL_Link", "URL_Title", "Source", "News_Type", "Primary_Companies", "Companies_Mentioned", "News_Tag", "Summary"])
search_term = st.text_input("Enter search term:")

if st.button("Search"):
    # Construct the query based on user input
    if search_term:
        if search_field == "URL Link":
            query = f"""SELECT * FROM news_articles WHERE 'URL Link' LIKE ?"""
        else:
            query = f"""SELECT * FROM news_articles WHERE {search_field} LIKE ?"""
        params = (f"%{search_term}%",)  # Escape user input to prevent SQL injection
    else:
        query = "SELECT * FROM news_articles"  # Return all data if no search term
        params = ()

    # Execute the query with parameters
    c.execute(query, params)

    # Fetch and display results
    results = c.fetchall()
    if results:
        st.write("Search results:")
        df = pd.DataFrame(results, columns=[desc[0] for desc in c.description])
        st.write(df)
    else:
        st.write("No results found.")

# Close the database connection
sqlite_connection.close()
