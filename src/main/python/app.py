import streamlit as st
import tempfile
from gptQnA import pdfGPT  # Assume your PdfProcessor class is in pdf_processor.py

# Initialize session state
if "pdf_processor" not in st.session_state:
    st.session_state.pdf_processor = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("PDF Chat Assistant")

# File Upload Section
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    # Create PdfProcessor instance and parse the PDF
    st.session_state.pdf_processor = pdfGPT(temp_path)
    st.session_state.pdf_processor.parse_pdf()
    st.session_state.pdf_processor.create_embeddings()
    st.success("PDF processed and embeddings created. You can now ask questions!")

# Chat Interface Section
if st.session_state.pdf_processor:
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if user_input := st.chat_input("Ask a question related to the uploaded PDF:"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.pdf_processor.ask(user_input)
                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
