import streamlit as st
import openai

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as OpenAILLM

# 🔐 Load the API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 📄 Streamlit UI setup
st.set_page_config(page_title="Chat with Your Notes", layout="wide")
st.title("Chat with Your Notes (PDF Q&A Bot)")

# 📁 File uploader
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # 📝 Save and parse the PDF
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader("temp.pdf")
    docs = loader.load()

    # 🔍 Split the PDF into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    # 💬 Ask user for query
    query = st.text_input("Ask a question about your PDF:")

    if query:
        with st.spinner("Generating answer..."):
            try:
                # 🔑 Generate embeddings ONLY after query is asked
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-ada-002",
                    openai_api_key=openai.api_key
                )
                store = FAISS.from_documents(chunks, embeddings)

                # 🤖 Load the QA chain
                llm = OpenAILLM(temperature=0, openai_api_key=openai.api_key)
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=store.as_retriever()
                )

                # 📤 Run the QA chain
                result = qa_chain.run(query)
                st.write("**Answer:**", result)

            except Exception as e:
                st.error("An error occurred. Please try again or reduce the size of your PDF.")
                st.exception(e)
