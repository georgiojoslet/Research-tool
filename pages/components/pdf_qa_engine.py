import os
import fitz  # PyMuPDF
import tempfile
from typing import List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

class GroqLLM(LLM):
    model: str = "llama3-8b-8192"
    api_key: str = os.getenv("GROQ_API_KEY", "")
    temperature: float = 0.0

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = Groq(api_key=self.api_key)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "groq-llm"


class PDFQAEngine:
    def __init__(self):
        self.qa_chain = None
        self.summary_text = ""

    def process_pdf(self, file_bytes):
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "uploaded.pdf")
        with open(pdf_path, "wb") as f:
            f.write(file_bytes)

        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])

        if not text.strip():
            raise RuntimeError("PDF text extraction failed — empty content.")

        txt_path = os.path.join(temp_dir, "temp.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        try:
            loader = TextLoader(txt_path, encoding="utf-8")
            documents = loader.load()
        except Exception as e:
            raise RuntimeError(f"Failed to load extracted text: {e}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embedding, persist_directory=os.path.join(temp_dir, "chroma_db"))

        retriever = vectorstore.as_retriever()
        groq_llm = GroqLLM()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=groq_llm,
            retriever=retriever,
            return_source_documents=True
        )

        summary_prompt = "Summarize what this document is about in 5-6 lines."
        self.summary_text = self.qa_chain({"query": summary_prompt})["result"]
        return self.summary_text

    def answer_question(self, query):
        if not self.qa_chain:
            return "Please process a PDF first."
        return self.qa_chain({"query": query})["result"]
