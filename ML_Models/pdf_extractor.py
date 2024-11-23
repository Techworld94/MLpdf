import os
import asyncio
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from dotenv import load_dotenv
import io

load_dotenv()

Google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=Google_api_key)

class PDFExtractor:
    def __init__(self, chunk_size=10000, chunk_overlap=1000):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def _extract_text_from_pdf(self, file_stream):
        """Asynchronously extracts text from a single PDF file using an in-memory file object."""
        try:
            text = ""
            with fitz.open(stream=file_stream, filetype="pdf") as pdf:
                for page in pdf:
                    text += page.get_text("text")
            if not text.strip():
                raise ValueError("No text extracted from the file. File may be corrupted.")
            return text
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")

    async def extract_text(self, file_streams):
        """Asynchronously extracts text from multiple in-memory file objects."""
        tasks = [self._extract_text_from_pdf(file_stream) for file_stream in file_streams]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pdf_texts = []
        for result, file_stream in zip(results, file_streams):
            if isinstance(result, Exception):
                print(f"Skipping file: {result}")
                continue
            pdf_texts.append(result)

        if not pdf_texts:
            raise ValueError("No text could be extracted from any of the files.")
        return " ".join(pdf_texts)

    def chunk_text(self, text):
        """Splits text into chunks based on the defined chunk size and overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        return text_splitter.split_text(text)

    def create_vector_store(self, text_chunks):
        """Creates a vector store from the text chunks using Google Generative AI embeddings."""
        if not text_chunks:
            raise ValueError("No valid text chunks to create vector store.")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        return vector_store