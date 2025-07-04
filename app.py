import streamlit as st
import openai

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as OpenAILLM

# 🔐 Add your OpenAI API key here
openai.api_key = "sk-REPLACE_WITH_YOUR_KEY"

st.set_page_config(page_title="Chat with Your Notes", layout="wide")
st.title("Chat with Your Notes (PDF Q&A Bot)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader("temp.pdf")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    store = FAISS.from_documents(chunks, embeddings)

    if "qa_chain" not in st.session_state:
        llm = OpenAILLM(temperature=0)
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=store.as_retriever()
        )

    query = st.text_input("Ask a question about your document:")
    if query:
        with st.spinner("Generating answer..."):
            res = st.session_state.qa_chain.run(query)
        st.write("**Answer:**", res)
