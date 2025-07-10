import os

import streamlit as st

from src.config import cfg

st.set_page_config(page_title="Policy Chatbot", layout="centered")

pdf_file = st.sidebar.file_uploader("Choose a PDF file", type=cfg.ALLOWED_EXTENSIONS)

if pdf_file is not None:
    if st.sidebar.button("Upload PDF"):
        processing_message = st.sidebar.text("Processing PDF...")
        try:
            os.makedirs(cfg.DATA_DIR, exist_ok=True)
            file_path = os.path.join(cfg.DATA_DIR, pdf_file.name)
            with open(file_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            processing_message.success("PDF uploaded successfully!")
        except Exception as e:
            processing_message.error(f"Error processing PDF: {e}")
