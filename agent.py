from llm import get_openai_model
from fetchFromDb import fetch_chunk_from_db
import json
import re
import os


def detect_image_paths(context_text):
    if not context_text:
        return []

    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".svg",
    ]

    patterns = [
        r'["\']?image_path["\']?\s*:\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
        r'["\']?(?:image_path|imagePath|image_url|imageUrl|img_path|imgPath|photo_path|photoPath|chart_path|chartPath)["\']?\s*[:=]\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
        r'(?:output_charts|charts|images|figures|plots)/[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
        r'[^\s"\']+/[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
        r'https?://[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
        r'"([^"]+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))"',
        r"'([^']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))'",
        r'["\'](?:image|img|photo|picture|chart|figure)["\']?\s*[:=]\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
    ]

    image_paths = []
    for pattern in patterns:
        matches = re.findall(pattern, context_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = next((m for m in match if m), match[0])
            match = match.strip("\"'")
            if match and match not in image_paths:
                image_paths.append(match)

    return image_paths


def is_query_informative(query: str) -> bool:
    if not query or len(query.strip()) < 3:
        return False
    trivial_queries = {
        "hi",
        "hello",
        "hey",
        "test",
        "ok",
        "okay",
        "what's up",
        "yo",
        "hmm",
        "who are you",
        "yes",
        "no",
    }
    return query.strip().lower() not in trivial_queries


def summarize_text(llm, text):
    """
    Summarize the input text using the LLM with a concise prompt.
    """
    if not text or len(text.strip()) == 0:
        return "No additional information."
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes text clearly and concisely.",
        },
        {
            "role": "user",
            "content": f"Summarize the following text clearly and concisely for explaining an image:\n\n{text}",
        },
    ]
    summary_response = llm.invoke(messages)
    return summary_response.content.strip()


# def handle_user_input(user_input):
#     try:
#         llm = get_openai_model()
#         context = None
#         chunks = None

#         # 1. Check if query is informative
#         if is_query_informative(user_input):
#             chunks = fetch_chunk_from_db(user_input)
#             if chunks and chunks.get("total_results", 0) > 0:
#                 context = json.dumps(chunks, indent=2)
#                 print("context",context)
#             else:
#                 print("No relevant context found in vector DB.")
#         else:
#             print("Query too generic or informal. Using general assistant mode.")

#         # 2. Detect image paths
#         image_paths = detect_image_paths(context) if context else []

#         # 3. Prepare image descriptions matching image_paths
#         image_contexts_raw = []
#         if chunks and "charts" in chunks:
#             chart_map = {
#                 c["image_path"]: c.get("content", "") for c in chunks.get("charts", [])
#             }
#             for img_path in image_paths:
#                 desc = chart_map.get(img_path, "No detailed description available.")
#                 image_contexts_raw.append(desc)
#         else:
#             image_contexts_raw = ["Image context not available." for _ in image_paths]

#         # 4. Summarize each image context
#         image_contexts_summarized = []
#         for raw_text in image_contexts_raw:
#             summary = summarize_text(llm, raw_text)
#             image_contexts_summarized.append(summary)

#         # 5. Prepare system message for LLM
#         if context:
#             system_message = (
#                 "You are a highly specialized research assistant.\n"
#                 "- Use the research context provided.\n"
#                 "- Cite context when answering.\n"
#                 "- If the context does not sufficiently answer the question, answer based on your general knowledge and state that clearly.\n"
#                 "- If you are not confident in the context, do NOT reference or mention any images or image paths from the context.\n"
#     )
#             if image_paths:
#                 system_message += (
#                     f"Context contains {len(image_paths)} image references.\n"
#                     f"After your answer, ask the user if they want to see the related images."
#                 )
#             user_msg = f"{user_input}\n\nRelevant research context:\n{context}\n\nPlease answer the question."
#         else:
#             system_message = "You are a helpful assistant with no extra context."
#             user_msg = user_input

#         # 6. Prepare messages and call LLM for main answer
#         messages = [
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": user_msg},
#         ]
#         response = llm.invoke(messages)

#         # 7. Return assistant text, image paths, and summarized image contexts4
#         print("image context summarized",image_contexts_summarized)
#         return response.content, image_paths, image_contexts_summarized

#     except Exception as e:
#         print("Error:", e)
#         return "Sorry, something went wrong.", [], []


def handle_user_input(user_input):
    try:
        llm = get_openai_model()
        context = None
        chunks = None

        # 1. Check if query is informative
        if is_query_informative(user_input):
            chunks = fetch_chunk_from_db(user_input)
            if chunks and chunks.get("total_results", 0) > 0:
                context = json.dumps(chunks, indent=2)
                print("context", context)
            else:
                print("No relevant context found in vector DB.")
        else:
            print("Query too generic or informal. Using general assistant mode.")

        # 2. Detect image paths
        image_paths = detect_image_paths(context) if context else []

        # 3. Prepare image descriptions matching image_paths
        image_contexts_raw = []
        if chunks and "charts" in chunks:
            chart_map = {
                c["image_path"]: c.get("content", "") for c in chunks.get("charts", [])
            }
            for img_path in image_paths:
                desc = chart_map.get(img_path, "No detailed description available.")
                image_contexts_raw.append(desc)
        else:
            image_contexts_raw = ["Image context not available." for _ in image_paths]

        # 4. Summarize each image context
        image_contexts_summarized = []
        for raw_text in image_contexts_raw:
            summary = summarize_text(llm, raw_text)
            image_contexts_summarized.append(summary)

        # 5. Prepare system message for LLM
        if context:
            system_message = (
                "You are a highly specialized research assistant.\n"
                "- Use the research context provided.\n"
                "- Cite context when answering.\n"
                "- If the context does not sufficiently answer the question, answer based on your general knowledge and state that clearly.\n"
                "- If you are not confident in the context, do NOT reference or mention any images or image paths from the context.\n"
            )
            if image_paths:
                system_message += (
                    f"Context contains {len(image_paths)} image references.\n"
                    f"After your answer, ask the user if they want to see the related images."
                )
            user_msg = f"{user_input}\n\nRelevant research context:\n{context}\n\nPlease answer the question."
        else:
            system_message = "You are a helpful assistant with no extra context."
            user_msg = user_input

        # 6. Prepare messages and call LLM for main answer
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_msg},
        ]
        response = llm.invoke(messages)
        response_text = response.content.strip()

        # 7. Confidence check: suppress images if assistant is not confident
        not_confident_phrases = [
            "based on my general knowledge",
            "not found in the provided context",
            "no relevant information",
            "no information found",
            "sorry, i cannot find",
            "not present in the context",
            "no data available",
        ]

        is_not_confident = any(
            phrase in response_text.lower() for phrase in not_confident_phrases
        )

        if is_not_confident:
            # suppress images when not confident
            return response_text, [], []
        else:
            # return images as usual
            print("image context summarized", image_contexts_summarized)
            return response_text, image_paths, image_contexts_summarized

    except Exception as e:
        print("Error:", e)
        return "Sorry, something went wrong.", [], []
