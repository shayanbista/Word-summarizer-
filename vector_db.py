import getpass
import os

from langchain_chroma import Chroma 

from utils import get_env_variable
from langchain_openai import OpenAIEmbeddings

import chromadb

persistent_client = chromadb.PersistentClient(path="./chroma_db")
collection = persistent_client.get_or_create_collection("collection_name")

api_key=get_env_variable('API_KEY')

if not api_key:
  os.environ["API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=api_key)

vector_store_from_client = Chroma(client=persistent_client,collection_name="collection_name",embedding_function=embeddings)



