from uuid import uuid4
from langchain_core.documents import Document as LCDocument
from langchain_community.vectorstores.utils import filter_complex_metadata
from vectorDb import vector_store_from_client


def Store(pages):
    try:
        ids = [str(uuid4()) for _ in pages]
        vector_store_from_client.add_documents(documents=pages, ids=ids)
        print("Documents stored successfully.")
    except Exception as e:
        print(f"Error occurred while storing vector: {e}")
        return False
