import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# 🔑 Configure Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# 📄 Streamlit UI setup
st.set_page_config(page_title="Chat with Your Notes", layout="wide")
st.title("📄 Chat With Your PDF")

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# 📁 File uploader
pdf = st.file_uploader("Upload a PDF", type="pdf")

if pdf:
    text = extract_pdf_text(pdf)
    st.success("✅ PDF content extracted.")

    # 📝 User question
    question = st.text_input("Ask a question based on the PDF:")

    if question:
        with st.spinner("💡 Thinking..."):
            prompt = f"Answer the question based on the following PDF content:\n\n{text}\n\nQuestion: {question}"
            try:
                response = model.generate_content(prompt)
                st.markdown("### 🧠 Answer:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Gemini API Error: {str(e)}")

