# pages/components/pdf_preview.py

import requests
import fitz  # PyMuPDF
import tempfile
from PIL import Image
import streamlit as st

def show_pdf_preview(pdf_url):
    try:
        response = requests.get(pdf_url)
        if response.status_code != 200:
            st.warning("Could not fetch PDF preview.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        doc = fitz.open(tmp_path)
        page = doc.load_page(0)  # First page
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        st.image(img, caption="📖 First Page Preview", use_container_width=True)
    except Exception as e:
        st.error(f"Preview failed: {e}")
