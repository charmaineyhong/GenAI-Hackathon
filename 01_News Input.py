import streamlit as st
import pandas as pd
import sqlite3
from utils.llm import get_completion

# Streamlit setup
st.title("News Input")

# Text input for URL
url_input = st.text_area("URLs", height=300)
columns = ['Category']
rows = ['URL Link', 'URL Title', 'Publication Date', 'Source', 'News Type', 'Primary Companies', 'Companies Mentioned', 'News Tag', 'Summary']
big_df = pd.DataFrame({'Category':rows})

if st.button("Analyze"):
    if url_input:
        urls = [url.strip() for url in url_input.split(',')]
        processed_urls = set()

        for url in urls:
            if url in processed_urls:
                st.write(f"URL '{url}' has already been processed.")
                continue

            user_input = f'" analyze the website and provide output without mentioning text in bracket :  url link : , url title: , publication date: , Source: , news type: (Auto OEM(original equipment manager), cell maker , market , cell maker and market  ) , primary companies : (company which the article is about) , companies mentioned (all company,brand,relevant owner names ) , news tag [most relavent from capacity announcement , corporate action , corporate development , fundraising , market commentary , partnership , product release], and summary of {url} , leave a line after every catagory and do not print anything in brackets '
            messages = [{"role": "user", "content": user_input}]
            response = get_completion(messages)

            raw_data = response.choices[0].message.content
            data_pointer = 0

            def get_one_field(raw_data, data_pointer):
                field_name = ''
                field_data = ''
                while raw_data[data_pointer] != ':':
                    field_name += raw_data[data_pointer]
                    data_pointer+=1
                data_pointer += 1
                while raw_data[data_pointer] != '\n':
                    field_data += raw_data[data_pointer]
                    data_pointer += 1
                data_pointer += 1
                # return two fields for storage, and data pointer for updating the data pointer state for next field
                return field_name.strip(), field_data.strip(), data_pointer 
            
            def get_all_field(raw_data, data_pointer):
                all_field_data = {}
                for i in range(8):
                    one_field_header, one_field_data, data_pointer = get_one_field(raw_data, data_pointer)
                    all_field_data[one_field_header] = one_field_data
                #hardcoding last field's output
                
                last_field_name = 'Summary'
                last_field_data = ''
                while raw_data[data_pointer] != ':':
                    #last_field_name += raw_data[data_pointer] parse through "Summary of <name>" without modifying last_field_name
                    data_pointer+=1
                data_pointer += 1
                while raw_data[data_pointer] != '.':
                    last_field_data += raw_data[data_pointer]
                    data_pointer += 1
                data_pointer += 1

                all_field_data[last_field_name.strip()] = last_field_data.strip()

                return all_field_data
            
            processed_data = get_all_field(raw_data, 0)

            df = pd.DataFrame({'Data': processed_data.values() })
            big_df=pd.concat([big_df,df],axis=1 , ignore_index=True)

            sqlite_connection = sqlite3.connect("news_database.db")
            sqlite_connection.execute("""CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                URL_Link TEXT,
                URL_Title TEXT,
                Publication_Date TEXT,
                Source TEXT,
                News_Type TEXT,
                Primary_Companies TEXT,
                Companies_Mentioned TEXT,
                News_Tag TEXT,
                Summary TEXT
        )""") 
            
            c = sqlite_connection.cursor()
            
            # Check if the URL Link already exists in the table
            c.execute("""SELECT * FROM news_articles WHERE URL_Link = ?""",
               (processed_data["URL Link"],),)
            
            row = c.fetchone()

            if row:  # If the URL Link doesn't exist, insert the data
                st.write("Data is already in Database!")
                sqlite_connection.commit()

            else:
                data_tuple = (
                    processed_data["URL Link"],
                    processed_data["URL Title"],
                    processed_data["Publication Date"],
                    processed_data["Source"],
                    processed_data["News Type"],
                    processed_data["Primary Companies"],
                    processed_data["Companies Mentioned"],
                    processed_data["News Tag"],
                    processed_data["Summary"],
                )
                c.execute(
                    """INSERT INTO news_articles ('URL_Link',
                    'URL_Title', 'Publication_Date', 'Source', 'News_Type',
                    'Primary_Companies', 'Companies_Mentioned', 'News_Tag', 'Summary') 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    data_tuple,
                )

                sqlite_connection.commit()
            sqlite_connection.close()
        st.write(big_df)
