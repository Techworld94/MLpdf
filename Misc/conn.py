from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

class MongoDBConnector:
    def __init__(self):
        """Initializes the MongoDB connection parameters."""
        load_dotenv() 
        self.user = os.environ.get("_MONGO_USERNAME")
        self.password = os.environ.get("_MONGO_PASSWORD")
        self.encoded_username = quote_plus(self.user)
        self.encoded_password = quote_plus(self.password)
        self.uri = f"mongodb+srv://{self.encoded_username}:{self.encoded_password}@clusterm.rfbe7.mongodb.net/?retryWrites=true&w=majority&appName=ClusterM"
        self.client = None

    def connect(self):
        """Establishes connection to MongoDB and tests it."""
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')  # Test connection
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def get_client(self):
        """Returns the MongoDB client."""
        if self.client is None:
            self.connect()
        return self.client
