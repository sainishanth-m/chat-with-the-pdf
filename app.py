import streamlit as st
import fitz # PyMuPDF
import google.generativeai as genai

# --- 1. CONFIGURATION AND SETUP ---

# Set up page configuration with the new title
st.set_page_config(
    page_title="Chat with your PDF", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 🔑 Configure Gemini API key from Streamlit secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # *** FIX: Using the stable model name 'gemini-2.5-flash' to resolve the 404 error ***
    model = genai.GenerativeModel("gemini-2.5-flash") 
except Exception as e:
    st.error("🚨 Configuration Error: GEMINI_API_KEY not found in Streamlit secrets.")
    st.stop()

# --- 2. CUSTOM CSS FOR CLEANER LOOK ---

# Inject custom CSS for a clean, centered main container
st.markdown("""
<style>
    /* Center the main content */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }

    /* Customize the header and title */
    h1 {
        font-weight: 700;
        color: #2e4a6e; /* A professional blue/grey */
    }
    
    /* Make the chat input look clean */
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
        border: 2px solid #ccc;
    }
    
    /* Custom styling for the AI messages */
    .st-chat-message-container.st-ai .stChatMessage {
        background-color: #f0f8ff; /* Light blue background for AI */
        border-left: 4px solid #4682b4; /* Stronger border for emphasis */
    }
    
</style>
""", unsafe_allow_html=True)


# --- 3. HELPER FUNCTIONS ---

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    """Extracts text from a PyMuPDF document."""
    text = ""
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    return text

# Function to generate AI response
def generate_response(prompt):
    """Generates content using the Gemini model with the PDF text as context."""
    try:
        # The generate_content call is made here
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Changed the error message to be more user-friendly
        st.error(f"Gemini API Error: Could not generate response. Please check your API key and model name.")
        print(f"Detailed Error: {e}") # Print detailed error to console for debugging
        return "An error occurred while generating the response."

# --- 4. STREAMLIT APPLICATION LOGIC ---

# Initialize session state for chat history and PDF content
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# --- Sidebar for Upload and Status ---
with st.sidebar:
    st.header("Upload Document 📁")
    st.markdown("Upload a PDF file to start the conversation.")

    pdf_uploader = st.file_uploader(
        "PDF File (Max 20MB)", 
        type="pdf", 
        accept_multiple_files=False, 
        key="pdf_uploader"
    )
    
    # Process the uploaded file
    if pdf_uploader is not None:
        if pdf_uploader != st.session_state.get("current_pdf"):
            st.session_state["current_pdf"] = pdf_uploader
            with st.spinner("Extracting text..."):
                st.session_state.pdf_text = extract_pdf_text(pdf_uploader)
                if st.session_state.pdf_text:
                    st.session_state.pdf_uploaded = True
                    st.session_state.messages = [] # Clear history for new document
                    st.success("✅ PDF loaded and ready!")
                else:
                    st.session_state.pdf_uploaded = False
                    st.error("Failed to extract text from PDF.")
    elif st.session_state.pdf_uploaded:
         st.info("🔄 PDF still loaded. Upload a new file to change documents.")

# --- Main Content Area ---
st.title("📄 Chat with your PDF")
st.markdown("---")

if not st.session_state.pdf_uploaded:
    st.info("👈 Please upload a PDF file in the sidebar to begin chatting.")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask a question about your document..."):
        # 1. Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Prepare full prompt for Gemini
        context = st.session_state.pdf_text
        full_prompt = f"Using ONLY the following context, answer the user's question concisely. If the information is not present, state that fact.\n\nContext:\n---{context}---\n\nQuestion: {prompt}"
        
        # 3. Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("💡 Thinking..."):
                ai_response = generate_response(full_prompt)
            st.markdown(ai_response)
        
        # 4. Save AI response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
