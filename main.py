import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

from fileProcessor import process_pdf_with_enhanced_charts

from vector_store import Store


def main():
    """
    Main function showing how to use the enhanced PDF processor
    """
    print("Processing PDF...")
    file_path = "./pdf files/2.pdf"
    split_pages = []
    chartData = []

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
        )

        # Step 1: Extract charts and text
        pdf_pages = process_pdf_with_enhanced_charts(
            file_path, output_dir="enhanced_output_charts", use_easyocr=True
        )

        # print(pdf_pages)

        for page in pdf_pages:
            for i, chunk in enumerate(pdf_pages):
                print(i)
                print(chunk)

        # for page in pdf_pages:
        #     # 1. Append existing text chunks first
        #     for chunk in page.get("chunks", []):
        #         split_pages.append({
        #             "text": chunk["text"],
        #             "metadata": {
        #                 "page": page["page"],
        #                 "chunk_number": chunk["chunk_number"],
        #                 # No chart info here because this is text chunk
        #             },
        #         })

        # 2. Then handle charts separately
        # for i, chart in enumerate(page.get("charts", []), start=1):
        #     chart_text = " ".join(
        #         [text_obj["text"] for text_obj in chart.get("raw_text", [])]
        #     ).strip()

        #     split_pages.append({
        #         "text": chart_text,
        #         "metadata": {
        #             "page": page["page"],
        #             "chart_number": i,
        #             "chart_type": chart.get("chart_type"),
        #             "image_path": chart.get("image_path"),
        #         },
        #     })

        #     # Optionally, keep a separate list of charts if needed

        # print(split_pages)

    except Exception as e:
        print(f"Error processing PDF: {e}")


if __name__ == "__main__":
    main()
