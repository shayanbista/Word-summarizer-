from uuid import uuid4

from langchain_core.documents import Document
# from vector_db import vectorDB

def vectorStore(pages):
    documents = [
        Document(
            page_content=page["text"],
            metadata={
                "page": page["page"],
                "chunk_number": page["chunk_number"],
                "source": "pdf"
            },
            id=f"{page['page']}_{page['chunk_number']}"
        )
        for page in pages
    ]

    print(documents)

    # uuids = [str(uuid4()) for _ in range(len(documents))]
    # vectorDB.add_documents(documents=documents, ids=uuids)



