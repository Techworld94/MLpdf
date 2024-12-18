import faiss
import numpy as np
import pickle
import base64
from bson.binary import Binary 
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
import os
from langdetect import detect
from Subscriptions.pricing import PricingValidator

class QueryBot:
    def __init__(self, faiss_index_path, subscription_type):
        """
        Initialize the QueryBot instance with the path to the FAISS index.
        """
        self.faiss_index_path = faiss_index_path
        self.vector_store = None
        self.subscription_type = subscription_type
        self.pricing_validator = PricingValidator(subscription_type)

    def load_vector_store(self, embedding_model):
        """
        Load the FAISS vector store by reading the index file directly.
        """
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)            
            if not os.path.exists(self.faiss_index_path):
                raise FileNotFoundError(f"FAISS index file not found at {self.faiss_index_path}")

            self.vector_store = FAISS.load_local(self.faiss_index_path, 
                                                 embeddings, 
                                                 allow_dangerous_deserialization=True)

        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise e
    
    def detect_language(self, text):
            """
            Detect the language of the input text using langdetect.
            """
            try:
                language = detect(text)
                print(f"Detected language: {language}")
                return language
            except Exception as e:
                print(f"Error detecting language: {e}")
                return "en"

    async def answer_question(self, user_question, chat_model):
        """
        Generate an answer based on the user question using the vector store and AI model.
        """
        print(f"Subscription Type: {self.subscription_type}")
        print(f"Vector Store: {self.vector_store}")

        if not self.vector_store:
            raise ValueError("Vector store not loaded. Please call load_vector_store() first.")
        
        detected_language = self.detect_language(user_question)
        if self.subscription_type == "Free" and detected_language != "en":
            return (
                "❌ Oops! This subscription level only supports English queries. "
                "✨ Upgrade to Plus to unlock support for all languages and other premium features! 🚀"
            )
        elif self.subscription_type == "Plus" and detected_language != "en":
            print("Plus subscription detected. Non-English query allowed.")
        
        try:
            docs = self.vector_store.similarity_search(user_question)
            print(f"Retrieved {len(docs)} documents from FAISS index.")
        except Exception as e:
            print(f"Error in similarity_search: {e}")
        
        if len(docs) == 0:
            return "No relevant information found in the documents."

        prompt_template = """
        Use the context below to answer the question in the same language as the question. If the context doesn't directly answer the question, 
        provide details related to the question based on the closest matching information found in the context. 
        Only say "answer is not available in the context" if there's no relevant information at all.

        Context:\n{context}\n
        Question:\n{question}\n

        Answer ({language}):
        """.replace("{language}", detected_language)

        model = ChatGoogleGenerativeAI(model=chat_model, temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        # Run the chain to generate the response
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        print(f"Generated Response: {response['output_text']}")
        return response["output_text"]