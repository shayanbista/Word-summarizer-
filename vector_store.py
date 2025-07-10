from uuid import uuid4
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from vector_db import vector_store_from_client


def Store(pages):
    try:

        print(pages[4])
        # documents = [
        #     Document(
        #         page_content=page["text"],
        #         metadata={
        #             "page": page["page"],
        #             "chunk_number": page["chunk_number"],
        #             "source": "pdf",
        #         },
        #     )
        #     for page in pages
        # ]

        # ids = [
        #     f"{doc.metadata['page']}_{doc.metadata['chunk_number']}"
        #     for doc in documents
        # ]
        # vector_store_from_client.add_documents(documents=documents, ids=ids)

        # print(f"Successfully stored {len(documents)} documents")
        # return True

    except Exception as e:
        print(f"Error occurred while storing vector: {e}")
        return False
