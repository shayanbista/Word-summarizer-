import getpass
import os

from utils import get_env_variable
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

try:
    api_key = get_env_variable("API_KEY")
    if not api_key:
        os.environ["API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
        api_key = os.environ["API_KEY"]

    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key=api_key,
    )

    qdrant_client = QdrantClient(host="127.0.0.1", port=6333)
    collection_name = "collection_name"
    vector_size = 1536  

    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    vector_store_from_client = Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
except Exception as e:
    print("Error occurred in initialization:", e)
