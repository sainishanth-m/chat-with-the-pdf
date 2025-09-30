📄 Chat with your PDF
A clean, responsive, and easy-to-use Streamlit web app that allows you to upload a PDF document and ask questions about its content using the Google Gemini model.

The UI/UX has been optimized for a smooth, chat-like experience.

🚀 Features
Clean Interface: File uploading is moved to a sidebar, keeping the main screen focused on the conversation.

Chat History: Maintains a continuous conversation flow for multiple follow-up questions.

Gemini-Powered Q&A: Uses Google's powerful gemini-1.5-flash-latest model to accurately extract and summarize information from the document text.

PyMuPDF Integration: Efficiently extracts text from the uploaded PDF.

🛠️ Tech Stack
UI Framework: Streamlit

AI Model: Google Gemini API (gemini-1.5-flash-latest)

PDF Processing: PyMuPDF (via fitz)

🔑 Setup Instructions
Dependencies: Ensure you have the required libraries installed:

pip install -r requirements.txt

API Key:

Create a Gemini API Key from Google AI Studio.

In your Streamlit environment (e.g., Streamlit Cloud), add the secret named GEMINI_API_KEY to your secrets file (.streamlit/secrets.toml):

# .streamlit/secrets.toml
GEMINI_API_KEY="YOUR_API_KEY_HERE" 

Run the App:

streamlit run app.py



