import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from fileProcessor import extract_pdf_content
from vector_store import Store


def match_chart_to_figure(chart, figure_data, chart_index):
    """
    Match a specific chart to its corresponding figure data
    """
    matched_data = {
        "figure_numbers": [],
        "figure_titles": [],
        "figure_descriptions": [],
        "chart_types": [],
        "data_mentioned": figure_data.get("data_mentioned", []),
    }

    if len(figure_data["figure_numbers"]) > chart_index:
        matched_data["figure_numbers"] = [figure_data["figure_numbers"][chart_index]]

    if len(figure_data["figure_titles"]) > chart_index:
        matched_data["figure_titles"] = [figure_data["figure_titles"][chart_index]]

    if len(figure_data["figure_descriptions"]) > chart_index:
        matched_data["figure_descriptions"] = [
            figure_data["figure_descriptions"][chart_index]
        ]

    if figure_data["chart_types"]:

        if len(figure_data["figure_descriptions"]) > chart_index:
            description = figure_data["figure_descriptions"][chart_index].lower()
            matched_types = []
            for chart_type in figure_data["chart_types"]:
                if chart_type in description:
                    matched_types.append(chart_type)
            matched_data["chart_types"] = (
                matched_types if matched_types else [figure_data["chart_types"][0]]
            )
        else:

            if len(figure_data["chart_types"]) > chart_index:
                matched_data["chart_types"] = [figure_data["chart_types"][chart_index]]
            else:
                matched_data["chart_types"] = [figure_data["chart_types"][0]]

    return matched_data


def enhance_chart_with_figure_data(chart, page_text, page_number, chart_index=0):
    """
    Enhance chart metadata with figure data extracted from text
    Enhanced version with proper chart-figure matching
    """
    figure_data = extract_figure_data_from_text(page_text)

    matched_figure_data = match_chart_to_figure(chart, figure_data, chart_index)

    enhanced_chart = chart.copy()

    # Add figure information if available
    if matched_figure_data["figure_numbers"]:
        enhanced_chart["figure_numbers"] = matched_figure_data["figure_numbers"]

    if matched_figure_data["figure_titles"]:
        # Use the matched title for this specific chart
        if not enhanced_chart.get("title"):
            enhanced_chart["title"] = matched_figure_data["figure_titles"][0]
        enhanced_chart["figure_titles"] = matched_figure_data["figure_titles"]

    if matched_figure_data["figure_descriptions"]:
        enhanced_chart["figure_descriptions"] = matched_figure_data[
            "figure_descriptions"
        ]

    if matched_figure_data["chart_types"]:
        enhanced_chart["detected_chart_types"] = matched_figure_data["chart_types"]
    else:
        # Default fallback
        enhanced_chart["detected_chart_types"] = ["chart"]

    if matched_figure_data["data_mentioned"]:
        enhanced_chart["data_mentioned"] = matched_figure_data["data_mentioned"]

    return enhanced_chart


def generate_enhanced_chart_description(chart):
    """
    Generate a more comprehensive chart description using extracted figure data
    """
    descriptions = []

    # Add figure numbers
    if chart.get("figure_numbers"):
        fig_refs = ", ".join([f"Figure {num}" for num in chart["figure_numbers"]])
        descriptions.append(f"referenced as {fig_refs}")

    # Add figure titles/captions
    if chart.get("figure_titles"):
        titles = "; ".join(chart["figure_titles"])
        descriptions.append(f"captioned: {titles}")

    # Add detected chart types
    if chart.get("detected_chart_types"):
        chart_types = ", ".join(chart["detected_chart_types"])
        descriptions.append(f"chart types: {chart_types}")

    # Add figure descriptions
    if chart.get("figure_descriptions"):
        desc = "; ".join(chart["figure_descriptions"])
        descriptions.append(f"description: {desc}")

    # Add data mentioned
    if chart.get("data_mentioned"):
        data = ", ".join(chart["data_mentioned"])
        descriptions.append(f"data values: {data}")

    # Add original chart information
    image_path = chart.get("image_path", "")
    if "chart" in image_path.lower():
        descriptions.append("chart visualization")
    if "figure" in image_path.lower():
        descriptions.append("figure diagram")

    # Add title information
    if chart.get("title"):
        descriptions.append(f"titled {chart['title']}")

    # Add label information
    if chart.get("labels"):
        labels = chart["labels"]
        if isinstance(labels, list):
            descriptions.append(f"with labels: {', '.join(labels)}")
        else:
            descriptions.append(f"with labels: {labels}")

    # Add value information
    if chart.get("values"):
        values = chart["values"]
        if isinstance(values, list) and len(values) > 0:
            descriptions.append(f"showing values: {', '.join(map(str, values[:5]))}")

    # Add region information
    if chart.get("region"):
        descriptions.append(f"located in region {chart['region']}")

    # Add comprehensive search terms
    search_terms = [
        "graph",
        "plot",
        "visualization",
        "data",
        "figure",
        "chart",
        "diagram",
        "illustration",
        "statistical",
        "analysis",
        "comparison",
        "pie chart",
        "bar chart",
        "line graph",
        "scatter plot",
        "histogram",
    ]
    descriptions.extend(search_terms)

    return " ".join(descriptions)


def extract_figure_context(page_text, chart_region, context_window=300):
    """
    Extract text context around figures, focusing on figure-related content
    """
    # Look for text around figure references
    fig_pattern = r"(?:Fig\.|Figure)\s+\d+[^.]*\.[^.]*\."
    fig_matches = list(re.finditer(fig_pattern, page_text, re.IGNORECASE))

    if fig_matches:
        # Use the context around figure references
        contexts = []
        for match in fig_matches:
            start = max(0, match.start() - context_window // 2)
            end = min(len(page_text), match.end() + context_window // 2)
            context = page_text[start:end].strip()
            contexts.append(context)
        return " ".join(contexts)

    # Fallback to general context
    words = page_text.split()
    total_words = len(words)
    context_start = max(0, total_words // 2 - context_window // 2)
    context_end = min(total_words, context_start + context_window)

    return " ".join(words[context_start:context_end])


def create_enhanced_chart_content(chart, page_text, page_number, chart_index=0):
    """
    Create enhanced searchable content for charts with figure data
    Updated to use chart-specific figure matching
    """
    # First enhance the chart with figure data (now chart-specific)
    enhanced_chart = enhance_chart_with_figure_data(
        chart, page_text, page_number, chart_index
    )

    content_parts = []

    # 1. Original chart text
    chart_text = [
        item["text"] for item in enhanced_chart.get("raw_text", []) if item.get("text")
    ]
    if chart_text:
        content_parts.append(" ".join(chart_text))

    # 2. Enhanced description with figure data
    description = generate_enhanced_chart_description(enhanced_chart)
    content_parts.append(description)

    # 3. Context from surrounding text (focused on figure-related content)
    context = extract_figure_context(page_text, enhanced_chart.get("region", []))
    if context:
        content_parts.append(f"Context: {context}")

    # 4. Page reference
    content_parts.append(f"appears on page {page_number}")

    # 5. Figure-specific information
    if enhanced_chart.get("figure_numbers"):
        fig_info = f"Figure {', '.join(enhanced_chart['figure_numbers'])}"
        content_parts.append(fig_info)

    if enhanced_chart.get("figure_descriptions"):
        fig_desc = " ".join(enhanced_chart["figure_descriptions"])
        content_parts.append(f"Figure description: {fig_desc}")

    return " ".join(content_parts), enhanced_chart


def extract_figure_data_from_text(text):
    """
    Extract figure information from text using regex patterns
    Enhanced to maintain order and better matching
    """
    figure_data = {
        "figure_numbers": [],
        "figure_titles": [],
        "figure_descriptions": [],
        "chart_types": [],
        "data_mentioned": [],
    }

    # Pattern 1: Figure references with full captions (improved)
    # This pattern captures the full figure caption including the description
    fig_pattern = r"(?:Fig\.|Figure)\s+(\d+)\.\s*([^.]*(?:\.[^.]*)*?)(?=\s*(?:Fig\.|Figure|\n\n|\Z))"
    fig_matches = re.findall(fig_pattern, text, re.IGNORECASE | re.DOTALL)

    for fig_num, full_caption in fig_matches:
        figure_data["figure_numbers"].append(fig_num)

        # Split caption into title and description
        sentences = full_caption.split(".")
        if sentences:
            title = sentences[0].strip()
            figure_data["figure_titles"].append(title)

            # Join remaining sentences as description
            if len(sentences) > 1:
                description = ". ".join(sentences[1:]).strip()
                if description:
                    figure_data["figure_descriptions"].append(description)
            else:
                figure_data["figure_descriptions"].append(title)

    # Pattern 2: Chart type detection (in order of appearance)
    chart_type_patterns = [
        ("pie", r"pie\s+chart|circular\s+chart"),
        ("bar", r"bar\s+chart|column\s+chart"),
        ("line", r"line\s+chart|line\s+graph"),
        ("scatter", r"scatter\s+plot|scatter\s+chart"),
        ("histogram", r"histogram"),
        ("box", r"box\s+plot|box\s+chart"),
        ("area", r"area\s+chart|area\s+graph"),
    ]

    # Find chart types in order of appearance
    chart_positions = []
    for chart_type, pattern in chart_type_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            chart_positions.append((match.start(), chart_type))

    # Sort by position in text and add to list
    chart_positions.sort(key=lambda x: x[0])
    figure_data["chart_types"] = [chart_type for _, chart_type in chart_positions]

    # Remove duplicates while preserving order
    seen = set()
    unique_chart_types = []
    for chart_type in figure_data["chart_types"]:
        if chart_type not in seen:
            seen.add(chart_type)
            unique_chart_types.append(chart_type)
    figure_data["chart_types"] = unique_chart_types

    # Pattern 3: Data/measurements mentioned
    data_patterns = [
        r"(\d+(?:\.\d+)?)\s*%",  # Percentages
        r"(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)",  # Time
        r"(\d+(?:\.\d+)?)\s*(?:items?|elements?|categories?)",  # Counts
        r"smallest\s+(?:item|element|value|portion)",  # Smallest references
        r"largest\s+(?:item|element|value|portion)",  # Largest references
    ]

    for pattern in data_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        figure_data["data_mentioned"].extend(matches)

    return figure_data


# Updated main function - the key change is passing chart_index
def main():
    """
    Enhanced main function with figure data extraction
    """
    print("Processing PDF with enhanced chart storage and figure data extraction...")
    file_path = "./pdf/1.pdf"

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
        )

        # Step 1: Extract charts and text
        pdf_pages = extract_pdf_content(file_path)

        documents = []

        for page in pdf_pages:
            page_number = page["page"]
            print(f"\n📄 Page {page_number}")

            # Get full page text for context
            raw_text = page.get("text", "")
            if len(raw_text.strip()) < 30:
                print("⚠️ Text too short, using OCR fallback")
                raw_text = " ".join([item["text"] for item in page.get("ocr_text", [])])
            else:
                print(f"✅ Raw text length: {len(raw_text)}")

            # Extract figure data from page text
            figure_data = extract_figure_data_from_text(raw_text)
            print(f"🔍 Figure data found: {figure_data}")

            # Process text chunks
            text_chunks = splitter.split_text(raw_text)
            print(f"📝 Split into {len(text_chunks)} text chunks")

            for i, chunk in enumerate(text_chunks):
                if chunk.strip():
                    print(f"📦 Text Chunk {i}: {chunk[:80]!r}...")
                    doc = Document(
                        page_content=chunk.strip(),
                        metadata={
                            "page": page_number,
                            "chunk_index": i,
                            "chunk_type": "text",
                            "has_chart": bool(page["charts"]),
                            "source_pdf": file_path,
                            "figure_data": figure_data,
                        },
                    )
                    documents.append(doc)

            # Process charts with enhanced content and figure data
            # KEY CHANGE: Pass chart_index to match charts to figures
            for chart_idx, chart in enumerate(page["charts"]):
                print(f"\n📊 Processing Chart {chart_idx + 1}: {chart['image_path']}")
                print(f"  ➤ Region: {chart['region']}")
                print(f"  ➤ Original Title: {chart.get('title')}")

                # Create enhanced content with figure data - NOW PASSING chart_idx
                enhanced_content, enhanced_chart = create_enhanced_chart_content(
                    chart, raw_text, page_number, chart_idx
                )

                print(f"  ➤ Enhanced title: {enhanced_chart.get('title')}")
                print(
                    f"  ➤ Detected chart types: {enhanced_chart.get('detected_chart_types')}"
                )
                print(f"  ➤ Figure numbers: {enhanced_chart.get('figure_numbers')}")
                print(f"  ➤ Enhanced content length: {len(enhanced_content)}")

                region = (
                    list(enhanced_chart["region"])
                    if isinstance(enhanced_chart["region"], tuple)
                    else enhanced_chart["region"]
                )

                # Create chart document with enhanced content and figure data
                chart_doc = Document(
                    page_content=enhanced_content,
                    metadata={
                        "page": page_number,
                        "image_path": enhanced_chart["image_path"],
                        "region": region,
                        "labels": enhanced_chart.get("labels"),
                        "values": enhanced_chart.get("values"),
                        "title": enhanced_chart.get("title"),
                        "source_pdf": enhanced_chart["source_pdf"],
                        "chunk_index": f"chart_{chart_idx}",
                        "chunk_type": "chart",
                        "chart_description": generate_enhanced_chart_description(
                            enhanced_chart
                        ),
                        "figure_numbers": enhanced_chart.get("figure_numbers"),
                        "figure_titles": enhanced_chart.get("figure_titles"),
                        "figure_descriptions": enhanced_chart.get(
                            "figure_descriptions"
                        ),
                        "detected_chart_types": enhanced_chart.get(
                            "detected_chart_types"
                        ),
                        "data_mentioned": enhanced_chart.get("data_mentioned"),
                    },
                )
                documents.append(chart_doc)

                # Create context document with figure-aware content
                if len(raw_text.strip()) > 100:
                    context_content = f"Chart context from page {page_number}: {raw_text[:800]}... This page contains a chart at region {region}."
                    if enhanced_chart.get("figure_numbers"):
                        context_content += f" Referenced as Figure {', '.join(enhanced_chart['figure_numbers'])}."

                    context_doc = Document(
                        page_content=context_content,
                        metadata={
                            "page": page_number,
                            "related_chart": enhanced_chart["image_path"],
                            "chunk_type": "chart_context",
                            "source_pdf": file_path,
                            "chunk_index": f"context_chart_{chart_idx}",
                            "figure_data": figure_data,
                        },
                    )
                    documents.append(context_doc)

        print(f"\n📋 Summary:")
        print(f"  Total documents created: {len(documents)}")

        # Store the documents
        print(f"\n💾 Storing {len(documents)} documents...")
        Store(documents)
        print("✅ Storage completed!")

    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
