#pdfextractor.py

import os
import asyncio
import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

Google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=Google_api_key)

class PDFExtractor:
    def __init__(self, chunk_size=10000, chunk_overlap=1000):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def _extract_text_from_pdf(self, pdf_path):
        """Asynchronously extracts text from a single PDF file using PyMuPDF."""
        text = ""
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text("text")
        return text

    async def extract_text(self, pdf_paths):
        """Asynchronously extracts text from multiple PDFs."""
        tasks = [self._extract_text_from_pdf(pdf) for pdf in pdf_paths]
        pdf_texts = await asyncio.gather(*tasks)
        return " ".join(pdf_texts)

    def chunk_text(self, text):
        """Splits text into chunks based on the defined chunk size and overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        return text_splitter.split_text(text)

    def create_vector_store(self, text_chunks):
        """Creates a vector store from the text chunks using Google Generative AI embeddings."""
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        save_path = "C:/Users/harihara.subramanian/Documents/MLpdf/ML_Models/Output/faiss_index"
        vector_store.save_local(save_path)
        return vector_store

#MLpdf.py

import asyncio
import glob
from pdf_extractor import PDFExtractor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PDF_FOLDER_PATH = r"C:\Users\harihara.subramanian\Documents\MLpdf\ML_Models\pdf_testings\*"
FAISS_INDEX_PATH = r"C:\Users\harihara.subramanian\Documents\MLpdf\ML_Models\Output\faiss_index"

async def main():
    extractor = PDFExtractor()
    pdf_files = glob.glob(PDF_FOLDER_PATH)
    print("Processing PDF files...")
    raw_text = await extractor.extract_text(pdf_files)
    text_chunks = extractor.chunk_text(raw_text)
    extractor.create_vector_store(text_chunks)
    print("PDF processing complete. Ready for questions.")

    while True:
        user_question = input("Ask a question from the PDF content (or type 'exit' to quit): ")
        if user_question.lower() == 'exit':
            print("Exiting...")
            break
        
        response = await answer_question(user_question)
        print("Reply:", response)

async def answer_question(user_question):
    """Handles querying the FAISS index and returning an answer based on a user question."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(user_question)

    # Define conversational chain
    prompt_template = """
    Use the context below to answer the question. If the context doesn't directly answer the question, provide details related to the question based on the closest matching information found in the context. Only say "answer is not available in the context" if there's no relevant information at all.\n\n
    Context:\n {context}?\n
    Question:\n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return response["output_text"]

if __name__ == "__main__":
    asyncio.run(main())