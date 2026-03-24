
#pip install langchain

#pip install openai

#pip install langchain-core

#pip install langchain-community

#pip install -U langchain-openai

#pip install chromadb

#pip install streamlit

#pip install python-dotenv

#pip install pandas


import streamlit as st

import pandas as pd

#from langchain_core.tools import tool

from langchain_chroma import Chroma

from langchain_community.vectorstores import FAISS

from langchain_core.messages import AIMessage,HumanMessage,SystemMessage

from langchain_openai import OpenAIEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import CharacterTextSplitter

from langchain_core.tools import create_retriever_tool

from langchain.agents import create_agent


import os

from dotenv import load_dotenv

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

OPENAI_API_KEY=os.environ['OPENAI_API_KEY']

#@st.cache_data
#PyPDFLoader('C:\\Hotel\\Items.pdf')
loaders = [
PyPDFLoader('Items.pdf'),
PyPDFLoader('Services.pdf')
]
pages = []
for loader in loaders:
    pages.extend(loader.load())

# Load the document, split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0, separator="\n")
documents = text_splitter.split_documents(pages)
chunks = text_splitter.split_documents(pages)

vectordb = FAISS.from_documents(documents, OpenAIEmbeddings
 (openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small"))

#vectordb.similarity_search(query)
#start
#from langchain.chains import RetrievalQA
from langchain_classic.chains import RetrievalQA

from langchain_core.prompts import PromptTemplate

from langchain_openai import ChatOpenAI

template = """

You are a helpful hotel receptionist. Use the following pieces of context to answer the question at the end.

If the items are not available, just say "sorry, we don't have the items available." If the items are available say "Bringing the items name right away."
Do not say anything else. Do not try to make up an answer. If the service is not available, just say "sorry, we don't have the service available." If the service is available say "Someone is coming to help you now."  
 
Use three sentences maximum, relevant analogies, and keep the answer as concise as possible.

Use the active voice, and speak directly to the reader using concise language.
{context}

Question: {question}

Helpful Answer:

"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

llm = ChatOpenAI(model_name="gpt-4.1", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

#start
#Title of App
st.title("🤖 AI Receptionist")
chat_placeholder = st.empty()

if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # Display chat messages from history on app rerun
with chat_placeholder.container():
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


def send_and_feedback():
    if st.session_state.messages:
        result = send_email(st.session_state.messages)
        if result is True:
            st.success("Notification sent successfully!")
        else:
            st.error(f"Error: {result}")
    else:
        st.warning("No chat history to send.")
    # Accept user input
if prompt := st.chat_input("Your roon number and how can i help you?", on_submit=send_and_feedback):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response from Chat models
        response = qa_chain.invoke({"query": prompt})
             
         # message_placeholder.markdown(response)
        with st.chat_message("assistant"):
            st.markdown(response["result"])
        # Add assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response["result"]})

            
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIG ---
SENDER_EMAIL = "dhammed2000@yahoo.com"
SENDER_PASSWORD = "bntnozfmqiebiooe"  #Password
RECEIVER_EMAIL = "dapo40@gmail.com"

# --- EMAIL FUNCTION ---
def send_email(chat_history):
    subject = "Customer Chat History"

    body = "\n\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history]
    )

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)

    