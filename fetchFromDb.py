from vector_db import vector_store_from_client


def fetch_chunk_from_db(input_query, k=5):
    """
    Smart search that provides the best mix of content types
    """
    results = vector_store_from_client.similarity_search(input_query, k=k)

    # Categorize results
    charts = []
    texts = []
    contexts = []

    for result in results:
        chunk_type = result.metadata.get("chunk_type", "text")

        if chunk_type == "chart":
            charts.append(
                {
                    "image_path": result.metadata.get("image_path"),
                    "page": result.metadata.get("page"),
                    "region": result.metadata.get("region"),
                    "title": result.metadata.get("title"),
                    "content": result.page_content,
                    "score": (
                        "high"
                        if input_query.lower() in result.page_content.lower()
                        else "medium"
                    ),
                }
            )
        elif chunk_type == "chart_context":
            contexts.append(
                {
                    "content": result.page_content,
                    "page": result.metadata.get("page"),
                    "chart_image_path": result.metadata.get("related_chart"),
                }
            )
        else:
            texts.append(
                {"content": result.page_content, "page": result.metadata.get("page")}
            )

    return {
        "charts": charts,
        "texts": texts,
        "contexts": contexts,
        "total_results": len(results),
    }


# print("result of db",fetch_chunk_from_db(" A Multiple Pie Chart: Share of Document Types Assigned"))
