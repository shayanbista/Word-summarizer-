import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from fileProcessor import extract_pdf_content
from vector_store import Store


# def match_chart_to_figure(chart, figure_data, chart_index):
#     matched_data = {
#         "figure_numbers": [],
#         "figure_titles": [],
#         "figure_descriptions": [],
#         "chart_types": [],
#         "data_mentioned": figure_data.get("data_mentioned", []),
#     }

#     if len(figure_data["figure_numbers"]) > chart_index:
#         matched_data["figure_numbers"] = [figure_data["figure_numbers"][chart_index]]
#     if len(figure_data["figure_titles"]) > chart_index:
#         matched_data["figure_titles"] = [figure_data["figure_titles"][chart_index]]
#     if len(figure_data["figure_descriptions"]) > chart_index:
#         matched_data["figure_descriptions"] = [figure_data["figure_descriptions"][chart_index]]

#     if figure_data["chart_types"]:
#         if len(figure_data["figure_descriptions"]) > chart_index:
#             description = figure_data["figure_descriptions"][chart_index].lower()
#             matched_types = [ct for ct in figure_data["chart_types"] if ct in description]
#             matched_data["chart_types"] = matched_types if matched_types else [figure_data["chart_types"][0]]
#         elif len(figure_data["chart_types"]) > chart_index:
#             matched_data["chart_types"] = [figure_data["chart_types"][chart_index]]
#         else:
#             matched_data["chart_types"] = [figure_data["chart_types"][0]]

#     return matched_data


def match_chart_to_figure(chart, figure_data, chart_index):
    matched_data = {
        "figure_numbers": [],
        "figure_titles": [],
        "figure_descriptions": [],
        "chart_types": [],
        "data_mentioned": figure_data.get("data_mentioned", []),
    }

    # Match figure number, title, and description based on index
    if chart_index < len(figure_data["figure_numbers"]):
        matched_data["figure_numbers"] = [figure_data["figure_numbers"][chart_index]]

    if chart_index < len(figure_data["figure_titles"]):
        matched_data["figure_titles"] = [figure_data["figure_titles"][chart_index]]

    if chart_index < len(figure_data["figure_descriptions"]):
        matched_data["figure_descriptions"] = [
            figure_data["figure_descriptions"][chart_index]
        ]

    # Match chart type from figure description if possible
    if figure_data["chart_types"]:
        if chart_index < len(figure_data["figure_descriptions"]):
            description = figure_data["figure_descriptions"][chart_index].lower()
            matched_types = [
                ct for ct in figure_data["chart_types"] if ct in description
            ]
            matched_data["chart_types"] = (
                matched_types if matched_types else [figure_data["chart_types"][0]]
            )
        elif chart_index < len(figure_data["chart_types"]):
            matched_data["chart_types"] = [figure_data["chart_types"][chart_index]]
        else:
            matched_data["chart_types"] = [figure_data["chart_types"][0]]
    else:
        matched_data["chart_types"] = ["chart"]  # Default fallback

    return matched_data


def enhance_chart_with_figure_data(chart, page_text, page_number, chart_index=0):
    figure_data = extract_figure_data_from_text(page_text)
    matched_figure_data = match_chart_to_figure(chart, figure_data, chart_index)
    enhanced_chart = chart.copy()

    if matched_figure_data["figure_numbers"]:
        enhanced_chart["figure_numbers"] = matched_figure_data["figure_numbers"]
    if matched_figure_data["figure_titles"]:
        if not enhanced_chart.get("title"):
            enhanced_chart["title"] = matched_figure_data["figure_titles"][0]
        enhanced_chart["figure_titles"] = matched_figure_data["figure_titles"]
    if matched_figure_data["figure_descriptions"]:
        enhanced_chart["figure_descriptions"] = matched_figure_data[
            "figure_descriptions"
        ]
    enhanced_chart["detected_chart_types"] = matched_figure_data["chart_types"] or [
        "chart"
    ]
    if matched_figure_data["data_mentioned"]:
        enhanced_chart["data_mentioned"] = matched_figure_data["data_mentioned"]

    return enhanced_chart


def generate_enhanced_chart_description(chart):
    descriptions = []

    if chart.get("figure_numbers"):
        descriptions.append(
            f"referenced as {', '.join(['Figure ' + num for num in chart['figure_numbers']])}"
        )
    if chart.get("figure_titles"):
        descriptions.append(f"captioned: {'; '.join(chart['figure_titles'])}")
    if chart.get("detected_chart_types"):
        descriptions.append(f"chart types: {', '.join(chart['detected_chart_types'])}")
    if chart.get("figure_descriptions"):
        descriptions.append(f"description: {'; '.join(chart['figure_descriptions'])}")
    if chart.get("data_mentioned"):
        descriptions.append(f"data values: {', '.join(chart['data_mentioned'])}")

    image_path = chart.get("image_path", "")
    if "chart" in image_path.lower():
        descriptions.append("chart visualization")
    if "figure" in image_path.lower():
        descriptions.append("figure diagram")

    if chart.get("title"):
        descriptions.append(f"titled {chart['title']}")

    if chart.get("labels"):
        labels = chart["labels"]
        label_str = ", ".join(labels) if isinstance(labels, list) else labels
        descriptions.append(f"with labels: {label_str}")

    if chart.get("values"):
        values = chart["values"]
        if isinstance(values, list) and values:
            descriptions.append(f"showing values: {', '.join(map(str, values[:5]))}")

    if chart.get("region"):
        descriptions.append(f"located in region {chart['region']}")

    descriptions.extend(
        [
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
    )

    return " ".join(descriptions)


def extract_figure_context(page_text, chart_region, context_window=300):
    fig_pattern = r"(?:Fig\.|Figure)\s+\d+[^.]*\.[^.]*\."
    fig_matches = list(re.finditer(fig_pattern, page_text, re.IGNORECASE))

    if fig_matches:
        return " ".join(
            [
                page_text[
                    max(0, m.start() - context_window // 2) : min(
                        len(page_text), m.end() + context_window // 2
                    )
                ].strip()
                for m in fig_matches
            ]
        )

    words = page_text.split()
    total_words = len(words)
    return " ".join(
        words[max(0, total_words // 2 - context_window // 2) :][:context_window]
    )


def create_enhanced_chart_content(chart, page_text, page_number, chart_index=0):
    enhanced_chart = enhance_chart_with_figure_data(
        chart, page_text, page_number, chart_index
    )
    content_parts = []

    chart_text = [
        item["text"] for item in enhanced_chart.get("raw_text", []) if item.get("text")
    ]
    if chart_text:
        content_parts.append(" ".join(chart_text))

    description = generate_enhanced_chart_description(enhanced_chart)
    content_parts.append(description)

    context = extract_figure_context(page_text, enhanced_chart.get("region", []))
    if context:
        content_parts.append(f"Context: {context}")

    content_parts.append(f"appears on page {page_number}")

    if enhanced_chart.get("figure_numbers"):
        content_parts.append(f"Figure {', '.join(enhanced_chart['figure_numbers'])}")
    if enhanced_chart.get("figure_descriptions"):
        content_parts.append(
            f"Figure description: {' '.join(enhanced_chart['figure_descriptions'])}"
        )

    return " ".join(content_parts), enhanced_chart


def extract_figure_data_from_text(text):
    figure_data = {
        "figure_numbers": [],
        "figure_titles": [],
        "figure_descriptions": [],
        "chart_types": [],
        "data_mentioned": [],
    }

    fig_pattern = r"(?:Fig\.|Figure)\s+(\d+)\.\s*([^.]*(?:\.[^.]*)*?)(?=\s*(?:Fig\.|Figure|\n\n|\Z))"
    fig_matches = re.findall(fig_pattern, text, re.IGNORECASE | re.DOTALL)

    for fig_num, full_caption in fig_matches:
        figure_data["figure_numbers"].append(fig_num)
        sentences = full_caption.split(".")
        title = sentences[0].strip()
        figure_data["figure_titles"].append(title)
        description = ". ".join(sentences[1:]).strip() if len(sentences) > 1 else title
        figure_data["figure_descriptions"].append(description)

    chart_type_patterns = [
        ("pie", r"pie\s+chart|circular\s+chart"),
        ("bar", r"bar\s+chart|column\s+chart"),
        ("line", r"line\s+chart|line\s+graph"),
        ("scatter", r"scatter\s+plot|scatter\s+chart"),
        ("histogram", r"histogram"),
        ("box", r"box\s+plot|box\s+chart"),
        ("area", r"area\s+chart|area\s+graph"),
    ]

    chart_positions = [
        (match.start(), chart_type)
        for chart_type, pattern in chart_type_patterns
        for match in re.finditer(pattern, text, re.IGNORECASE)
    ]

    chart_positions.sort()
    seen = set()
    for _, chart_type in chart_positions:
        if chart_type not in seen:
            seen.add(chart_type)
            figure_data["chart_types"].append(chart_type)

    data_patterns = [
        r"(\d+(?:\.\d+)?)\s*%",
        r"(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)",
        r"(\d+(?:\.\d+)?)\s*(?:items?|elements?|categories?)",
        r"smallest\s+(?:item|element|value|portion)",
        r"largest\s+(?:item|element|value|portion)",
    ]

    for pattern in data_patterns:
        figure_data["data_mentioned"].extend(re.findall(pattern, text, re.IGNORECASE))

    return figure_data


def process_pdf(pdf):
    pdf_path = ""
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
        )

        if hasattr(pdf, "read"):
            upload_dir = "temp_uploads"
            os.makedirs(upload_dir, exist_ok=True)
            pdf_path = os.path.join(upload_dir, pdf.name)
            with open(pdf_path, "wb") as f:
                f.write(pdf.read())
        else:
            pdf_path = pdf

        pdf_pages = extract_pdf_content(pdf_path)
        print("pdf pages", pdf_pages)
        documents = []

        for page in pdf_pages:
            page_number = page["page"]
            raw_text = page.get("text", "")
            if len(raw_text.strip()) < 30:
                raw_text = " ".join([item["text"] for item in page.get("ocr_text", [])])

            figure_data = extract_figure_data_from_text(raw_text)
            text_chunks = splitter.split_text(raw_text)

            for i, chunk in enumerate(text_chunks):
                if chunk.strip():
                    documents.append(
                        Document(
                            page_content=chunk.strip(),
                            metadata={
                                "page": page_number,
                                "chunk_index": i,
                                "chunk_type": "text",
                                "has_chart": bool(page["charts"]),
                                "source_pdf": pdf,
                                "figure_data": figure_data,
                            },
                        )
                    )

            for chart_idx, chart in enumerate(page["charts"]):
                enhanced_content, enhanced_chart = create_enhanced_chart_content(
                    chart, raw_text, page_number, chart_idx
                )
                region = (
                    list(enhanced_chart["region"])
                    if isinstance(enhanced_chart["region"], tuple)
                    else enhanced_chart["region"]
                )

                documents.append(
                    Document(
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
                )

                if len(raw_text.strip()) > 100:
                    context_content = f"Chart context from page {page_number}: {raw_text[:800]}... This page contains a chart at region {region}."
                    if enhanced_chart.get("figure_numbers"):
                        context_content += f" Referenced as Figure {', '.join(enhanced_chart['figure_numbers'])}."

                    documents.append(
                        Document(
                            page_content=context_content,
                            metadata={
                                "page": page_number,
                                "image_path": enhanced_chart["image_path"],
                                "chunk_type": "chart_context",
                                "source_pdf": pdf,
                                "chunk_index": f"context_chart_{chart_idx}",
                                "figure_data": figure_data,
                            },
                        )
                    )
        Store(documents)
        # print("documents",documents)

    except Exception as e:
        import traceback

        traceback.print_exc()
