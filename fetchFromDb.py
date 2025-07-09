from vector_db import vector_store_from_client


def fetch_chunk_from_db(input):

    resultContent = []
    results = vector_store_from_client.similarity_search(
        input,
        k=2,
        filter={"source": "pdf"},
    )

    for result in results:
        resultContent = [result.page_content]
    return resultContent
