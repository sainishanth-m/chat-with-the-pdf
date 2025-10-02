import streamlit as st
import fitz # PyMuPDF
import google.generativeai as genai

# --- 1. CONFIGURATION AND SETUP ---

st.set_page_config(
    page_title="Chat with your PDF!", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Ensure sidebar is collapsed by default for the clean look
)

# 🔑 Configure Gemini API key from Streamlit secrets
try:
    # Using the stable model: gemini-2.5-flash
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash") 
except Exception:
    # This block handles the case where the API key might be missing in secrets
    pass 

# Initialize session state for chat history and PDF content
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# --- 2. CUSTOM CSS INJECTION ---

# Custom CSS to match the Paperpal aesthetic
st.markdown("""
<style>
    /* General Page Layout and Font */
    body {
        font-family: 'Inter', sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
    }
    
    /* Center the Main Content */
    .st-emotion-cache-z5fcl4 {
        justify-content: center;
    }

    /* Primary Blue Color */
    :root {
        --primary-blue: #007bff;
        --light-blue: #e0f0ff;
        --dark-text: #2c3e50;
    }

    /* Landing Header Styling */
    .landing-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--dark-text);
        text-align: center;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .landing-subheader {
        font-size: 1.25rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 50px;
    }
    .pdf-word {
        color: white;
        background-color: var(--primary-blue);
        padding: 5px 12px;
        border-radius: 10px;
        display: inline-block;
        font-size: 3.2rem;
        line-height: 1.2;
        margin-left: 10px;
    }
    
    /* Custom Upload Box */
    .upload-box-container {
        border: 2px dashed var(--primary-blue);
        border-radius: 15px;
        padding: 60px 40px;
        text-align: center;
        background-color: var(--light-blue);
        max-width: 800px;
        margin: 0 auto;
        margin-bottom: 50px;
    }
    .stFileUploader {
        border: none !important; 
        background-color: transparent !important;
    }
    .st-emotion-cache-1cypcdp { /* Streamlit file uploader button container */
        border: none !important;
        background-color: transparent !important;
        padding: 0;
        margin-top: 20px;
        
    }
    .st-emotion-cache-13m7zvx { /* Streamlit Upload button */
        background-color: var(--primary-blue);
        color: white;
        font-size: 18px;
        padding: 10px 30px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s;
        
    }
    
    /* Custom Feature Cards */
    .feature-card {
        padding: 30px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        height: 100%;
        border: 1px solid #eee;
    }
    .feature-icon-circle {
        background-color: var(--light-blue);
        color: var(--primary-blue);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        margin-bottom: 15px;
    }
    
    /* FAQ Accordion Styling (Overriding Streamlit's Expander) */
    .st-emotion-cache-wugj2v { /* Streamlit Expander Container */
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: none;
    }
    .st-emotion-cache-1n64x57 { /* Expander Header/Title */
        font-weight: 600;
        color: var(--dark-text);
        padding: 15px;
    }
    .st-emotion-cache-1215l3e { /* Expander Content */
        padding: 15px;
        border-top: 1px solid #eee;
    }
    
    /* Custom Blue Button for Try Now */
    .try-now-button {
        background-color: var(--primary-blue);
        color: white;
        font-size: 18px;
        padding: 12px 40px;
        border-radius: 8px;
        border: none;
        display: inline-block;
        margin-top: 30px;
        text-decoration: none;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 123, 255, 0.4);
    }
    
    /* Chat Interface Styling (for after upload) */
    .chat-interface .st-emotion-cache-1r650ly { /* Title for chat mode */
        text-align: left;
        font-size: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. HELPER FUNCTIONS ---

def extract_pdf_text(pdf_file):
    """Extracts text from a PyMuPDF document."""
    text = ""
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.session_state.pdf_uploaded = False
        st.error(f"Error reading PDF: {e}")
        return None
    return text

def generate_response(prompt):
    """Generates content using the Gemini model with the PDF text as context."""
    # Safety check for configuration
    try:
        if not genai.get_default_model():
            return "Configuration Error: Gemini API key is missing. Please check your Streamlit secrets."
    except:
        return "Configuration Error: Gemini API key is missing. Please check your Streamlit secrets."
        
    if not st.session_state.pdf_text:
        return "Please upload and process a PDF first."
        
    context = st.session_state.pdf_text
    full_prompt = f"Using ONLY the following context, answer the user's question concisely. If the information is not present, state that fact.\n\nContext:\n---{context}---\n\nQuestion: {prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error: Could not generate response. Error: {str(e)}"

# --- 4. MAIN LANDING PAGE RENDER ---

def render_landing_page():
    
    st.markdown("""
        <div class="landing-header">
            Chat with any <span class="pdf-word">PDF!</span>
        </div>
        <p class="landing-subheader">
            Deep-dive research in seconds—just upload and ask anything.
        </p>
    """, unsafe_allow_html=True)
    
    # ----------------------------------
    # 1. Main Upload Box (Styled)
    # ----------------------------------
    with st.container():
        st.markdown('<div class="upload-box-container">', unsafe_allow_html=True)
        
        # Streamlit requires the actual uploader component for file handling
        
        # Display custom icon/text above the uploader
        st.markdown("""
            <p style='color: #7f8c8d; margin-bottom: 20px;'>Click to upload, or drag PDF here</p>
        """, unsafe_allow_html=True)
        
        # The actual file uploader component
        pdf = st.file_uploader(
            "Upload a PDF", 
            type="pdf",
            accept_multiple_files=False, 
            label_visibility="collapsed",
            key="landing_pdf_uploader"
        )
        
        st.markdown("<p style='color: #7f8c8d; font-size: 0.9rem; margin-top: 10px;'>Maximum Size 25MB</p>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    if pdf:
        with st.spinner("Processing PDF and extracting text..."):
            st.session_state.pdf_text = extract_pdf_text(pdf)
            if st.session_state.pdf_text:
                st.session_state.pdf_uploaded = True
                st.session_state.messages = [] # Clear history
                st.experimental_rerun() # Rerun to switch to chat mode
            
    st.markdown("---")
    
    # ----------------------------------
    # 2. Why Use Section (4 Cards)
    # ----------------------------------
    st.markdown("""
        <h2 style='text-align: center; color: var(--dark-text); font-size: 2.5rem; font-weight: 700; margin-top: 50px; margin-bottom: 20px;'>
            Why Students and Researchers Use Paperpal's Chat PDF?
        </h2>
        <p style='text-align: center; color: #7f8c8d; font-size: 1.1rem; max-width: 800px; margin: 0 auto 50px;'>
            Our free AI chat with any PDF tool acts as a trusted research assistant, generating insights with links to source material.
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-circle">📜</div>
                <h3 style='font-weight: 600; color: var(--dark-text);'>Summarize Lengthy Papers</h3>
                <p style='color: #7f8c8d; font-size: 0.9rem;'>Make your reading more efficient with our free document summarizer, which provides an accurate summary covering all key points.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-circle">📋</div>
                <h3 style='font-weight: 600; color: var(--dark-text);'>Copy Text with Citations</h3>
                <p style='color: #7f8c8d; font-size: 0.9rem;'>Scroll through full-text PDFs and copy relevant text with accompanying citations, allowing you to easily add accurate references.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-circle">✅</div>
                <h3 style='font-weight: 600; color: var(--dark-text);'>Discover Related Literature</h3>
                <p style='color: #7f8c8d; font-size: 0.9rem;'>Use the AI PDF reader to find relevant articles that support or challenge your research hypothesis, broadening your perspective.</p>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon-circle">✍️</div>
                <h3 style='font-weight: 600; color: var(--dark-text);'>Accelerate Writing Workflows</h3>
                <p style='color: #7f8c8d; font-size: 0.9rem;'>Combine Chat PDF with other Paperpal features to write better, cite accurately, and polish your language in half the time.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <div style='text-align: center; margin-top: 40px;'>
            <a href="#landing_pdf_uploader" class="try-now-button">Try Now - It's Free</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ----------------------------------
    # 3. How to Use (4 Steps Flow)
    # ----------------------------------
    st.markdown("""
        <h2 style='text-align: center; color: var(--dark-text); font-size: 2.5rem; font-weight: 700; margin-top: 50px; margin-bottom: 50px;'>
            Ask PDFs anything and get verified insights that help streamline research workflows.
        </h2>
    """, unsafe_allow_html=True)
    
    col_steps = st.columns(7) # Use 7 columns for 4 steps + 3 separators

    def render_step(col, icon, title, text):
        with col:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <div style='background-color: var(--primary-blue); color: white; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; font-size: 28px; margin-bottom: 20px;'>{icon}</div>
                    <h3 style='font-weight: 600; color: var(--dark-text); margin-bottom: 10px;'>{title}</h3>
                    <p style='color: #7f8c8d; font-size: 0.9rem;'>{text}</p>
                </div>
            """, unsafe_allow_html=True)

    render_step(col_steps[0], "⬆️", "Upload PDFs", "Upload any PDF, interact with PDFs saved to your citation library, or select full-text papers from our research repository.")
    col_steps[1].markdown("<div style='text-align: center; font-size: 2rem; color: #ddd; margin-top: 50px;'>---</div>", unsafe_allow_html=True) # Separator
    render_step(col_steps[2], "❓", "Ask Questions", "Choose from the pre-set prompts or type in your question for our AI to analyze PDFs and generate a response.")
    col_steps[3].markdown("<div style='text-align: center; font-size: 2rem; color: #ddd; margin-top: 50px;'>---</div>", unsafe_allow_html=True) # Separator
    render_step(col_steps[4], "📄", "Review Outputs", "Use source links provided with the AI-generated output to quickly check insights and identify key points within the PDF.")
    col_steps[5].markdown("<div style='text-align: center; font-size: 2rem; color: #ddd; margin-top: 50px;'>---</div>", unsafe_allow_html=True) # Separator
    render_step(col_steps[6], "➕", "Save to Notes", "Copy and save relevant snippets with accurate in-text, full citations to your notes.")

    st.markdown("""
        <div style='text-align: center; margin-top: 50px;'>
            <a href="#landing_pdf_uploader" class="try-now-button">Upload PDF</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ----------------------------------
    # 4. FAQ Section (Accordion Style)
    # ----------------------------------
    st.markdown("""
        <h2 style='text-align: center; color: var(--dark-text); font-size: 2.5rem; font-weight: 700; margin-top: 50px; margin-bottom: 30px;'>
            Frequently Asked Questions
        </h2>
    """, unsafe_allow_html=True)
    
    faq_content = [
        {
            "question": "What is Paperpal Chat PDF used for?", 
            "answer": "Paperpal’s Chat PDF tool helps you summarize full-text research papers, understand new/complex topics, and organize your notes effortlessly. It saves hours of time spent on literature reviews, helps you extract key insights in minutes, and even lets you generate MCQ questions for your assignments. Whether analyzing technical reports or breaking down research papers, Paperpal’s free AI Chat with PDF tool can help you read smarter, learn faster, and become more efficient."
        },
        {
            "question": "How accurate are Paperpal's Chat PDF responses?", 
            "answer": "Responses are highly accurate because the underlying Gemini AI model is restricted to using *only* the content extracted from your uploaded PDF. This prevents the model from generating information (hallucinating) outside of the source material."
        },
        {
            "question": "Can I use Paperpal Chat PDF for free?", 
            "answer": "Yes, basic access to the Chat with PDF tool is available for free, allowing users to upload documents and begin immediate conversations with the AI."
        },
        {
            "question": "How secure is my work – Does Paperpal save your PDFs?", 
            "answer": "Your privacy is paramount. When using this Streamlit application, the PDF content is only stored temporarily in the application's memory (`st.session_state`) during your session and is deleted when the session ends or a new PDF is uploaded."
        },
        {
            "question": "Does Paperpal have any limit on file type or number of files uploaded?", 
            "answer": "This application currently only supports **one PDF file** at a time due to the context window limitations of the underlying AI model. The maximum file size is limited by Streamlit's default upload limit, typically around 200MB, but 25MB is a good practical limit."
        },
    ]

    for item in faq_content:
        with st.expander(item['question']):
            st.markdown(f"<p style='color: #495057;'>{item['answer']}</p>", unsafe_allow_html=True)

# --- 5. CHAT INTERFACE RENDER ---

def render_chat_interface():
    # Overwrite the page content with the chat interface
    st.markdown("<div class='chat-interface'>", unsafe_allow_html=True)
    st.title("📄 Chat with your PDF")
    st.markdown("---")

    # Sidebar for document status (optional, but good for context)
    with st.sidebar:
        st.success("✅ PDF loaded and ready!")
        st.info("Start asking questions below. The AI will only use content from the document.")
        # Provide option to upload new file to leave chat mode
        if st.button("Upload New PDF"):
            st.session_state.pdf_uploaded = False
            st.session_state.pdf_text = None
            st.session_state.messages = []
            st.experimental_rerun()
            
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

        # 2. Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("💡 Thinking..."):
                ai_response = generate_response(prompt)
            st.markdown(ai_response)
        
        # 3. Save AI response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    st.markdown("</div>", unsafe_allow_html=True)


# --- 6. EXECUTION LOGIC ---

if st.session_state.pdf_uploaded:
    render_chat_interface()
else:
    render_landing_page()
