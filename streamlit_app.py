import os

import streamlit as st

from config import config

st.set_page_config(page_title="Policy Chatbot", layout="centered")

pdf_file = st.sidebar.file_uploader("Choose a PDF file", type=config.ALLOWED_EXTENSIONS)

if pdf_file is not None:
    if st.sidebar.button("Upload PDF"):
        processing_message = st.sidebar.text("Processing PDF...")
        try:
            os.makedirs(config.DATA_DIR, exist_ok=True)
            file_path = os.path.join(config.DATA_DIR, pdf_file.name)
            with open(file_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            processing_message.success("PDF uploaded successfully!")
        except Exception as e:
            processing_message.error(f"Error processing PDF: {e}")
