import sqlite3
import tempfile
from io import StringIO
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.llm import get_completion

def dump_to_text(sqlite_file, query):
    # Connect to the SQLite database
    conn = sqlite3.connect('news_database.db')
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch all the data
    data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Use StringIO for temporary string creation
    output_string = StringIO()
    for row in data:
        # Encode as bytes for writing to a file stream
        row_str = ','.join(map(str, row)) + '\n'  # Ensure string formatting before encoding
        output_string.write(row_str)

    # Get the value of the StringIO buffer
    output_data = output_string.getvalue()

    # Close the StringIO object
    output_string.close()

    return output_data

# Q&A Template
QNA_TEMPLATE = """Use the following pieces of context to answer the question at the end
{context}
QUESTION: {question}
ANSWER (with APA citations):
EXAMPLE ANSWER: <...> (APA Citation) (URL) (Date)"""

@st.cache_resource
def load_embeddings():
    # equivalent to SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

embeddings = load_embeddings()
file_raw_text = ""

#page title
st.title("Ask Anything!")

#customizing side bar -> this will improve the gpt's knowledge if system knowledge is changed.
with st.sidebar:
    sys_message = st.text_area("System message", value="You are a helpful assistant.")
    top_k = st.slider("Top k chunk docs to use", value=3, min_value=1, max_value=5)

qna_prompt = st.text_area("Prompt Example:", value=QNA_TEMPLATE, height=150)
if user_input := st.text_area("Your Question"):
    context = file_raw_text
    updated_input = qna_prompt.format(context=context, question=user_input)
    messages = [
        {"role": "system", "content": sys_message},
        {"role": "user", "content": updated_input},
        ]
    
    response = get_completion(messages)
    reply = response.choices[0].message.content
    st.write(reply.replace("$", r"\$"))
st.button("Ask!")