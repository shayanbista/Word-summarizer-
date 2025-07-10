import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from fileProcessor import extract_pdf_content
from vector_store import Store


def main():
    """
    Main function showing how to use the enhanced PDF processor
    """
    print("Processing PDF...")
    file_path = "./pdf files/piee.pdf"
    split_pages = []
    chartData = []

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
        )

        # Step 1: Extract charts and text
        pdf_pages = extract_pdf_content(file_path)

        documents = []
        for page in pdf_pages[:4]:
            print(f"\n📄 Page {page['page']}")

            raw_text = page.get("text", "")
            if len(raw_text.strip()) < 30:
                print("⚠️ Text too short, using OCR fallback")
                raw_text = " ".join([item["text"] for item in page.get("ocr_text", [])])
            else:
                print(f"✅ Raw text length: {len(raw_text)}")
            text_chunks = splitter.split_text(raw_text)
            print(f" Split into {len(text_chunks)} chunks")
            for i, chunk in enumerate(text_chunks):
                if chunk.strip():
                    print(f"\n📦 Chunk {i}: {chunk[:120]!r}")
                    doc = Document(
                        page_content=chunk.strip(),
                        metadata={
                            "page": page["page"],
                            "chunk_index": i,
                            "has_chart": bool(page["charts"]),
                        },
                    )
                    documents.append(doc)
                else:
                    print(f"⚠️ Empty chunk at index {i}, skipping.")

                    # Step 4: Add each chart with inspection
            for chart in page["charts"]:
                print(f"\n📊 Chart: {chart['image_path']}")
                print(f"  ➤ Region: {chart['region']}")
                print(f"  ➤ Title: {chart.get('title')}")
                print(f"  ➤ Labels: {chart.get('labels')}")
                print(f"  ➤ Values: {chart.get('values')}")

                chart_text = [
                    item["text"]
                    for item in chart.get("raw_text", [])
                    if item.get("text")
                ]
                page_content = " ".join(chart_text)

                region = (
                    list(chart["region"])
                    if isinstance(chart["region"], tuple)
                    else chart["region"]
                )

                doc = Document(
                    page_content=page_content,
                    metadata={
                        "page": page["page"],
                        "image_path": chart["image_path"],
                        "region": region,
                        "labels": chart.get("labels"),
                        "values": chart.get("values"),
                        "title": chart.get("title"),
                        "source_pdf": chart["source_pdf"],
                        "chunk_index": f"chart_{chart['image_path'].split('_')[-1].replace('.png','')}",
                    },
                )
                documents.append(doc)
            Store(documents)

    except Exception as e:
        print(f"Error processing PDF: {e}")


if __name__ == "__main__":
    main()
