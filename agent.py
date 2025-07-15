
# from llm import get_openai_model
# from fetchFromDb import fetch_chunk_from_db
# import json
# import re
# import os

# # displayed_images = set()

# # def is_query_informative(query: str) -> bool:
# #     """
# #     Filters out vague or trivial queries that are not worth sending to the vector DB.
# #     """
# #     if not query or len(query.strip()) < 3:
# #         return False
# #     trivial_queries = {"hi", "hello", "hey", "test", "ok", "what's up", "yo", "hmm", "who are you"}
# #     return query.strip().lower() not in trivial_queries

# def detect_image_paths(context_text):
#     if not context_text:
#         return []
    
#     image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
    
#     patterns = [
#         r'["\']?image_path["\']?\s*:\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
#         r'["\']?(?:image_path|imagePath|image_url|imageUrl|img_path|imgPath|photo_path|photoPath|chart_path|chartPath)["\']?\s*[:=]\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
#         r'(?:output_charts|charts|images|figures|plots)/[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
#         r'[^\s"\']+/[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
#         r'https?://[^\s"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg)',
#         r'"([^"]+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))"',
#         r"'([^']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))'",
#         r'["\'](?:image|img|photo|picture|chart|figure)["\']?\s*[:=]\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|tiff|webp|svg))["\']?',
#     ]
    
#     image_paths = []
#     for pattern in patterns:
#         matches = re.findall(pattern, context_text, re.IGNORECASE)
#         for match in matches:
#             if isinstance(match, tuple):
#                 match = next((m for m in match if m), match[0])
#             match = match.strip('"\'')
#             if match and match not in image_paths:
#                 image_paths.append(match)
    
#     return image_paths

# # def handle_user_input(user_input):
# #     try:
# #         llm = get_openai_model()
# #         context = None
# #         chunks = None

# #         if is_query_informative(user_input):
# #             chunks = fetch_chunk_from_db(user_input)
# #             print("chunks",chunks)
# #             if chunks and chunks.get("total_results", 0) > 0:
# #                 context = json.dumps(chunks, indent=2)
# #             else:
# #                 print("No relevant context found in vector DB.")
# #         else:
# #             print("Query too generic or informal. Using general assistant mode.")

# #         image_paths = detect_image_paths(context) if context else []
# #         print("imagepaths",image_paths)

# #         print("Context available:", bool(context))
# #         if context:
# #             print("Context preview:", context[:200] + "..." if len(context) > 200 else context)

# #         if context:
# #             system_message = (
# #                 "You are a highly specialized research assistant.\n"
# #                 "- You have access to relevant research context below.\n"
# #                 "- When answering, first consider if you are confident enough to answer based on your own knowledge.\n"
# #                 "- If confident, answer using your own knowledge and clearly state so.\n"
# #                 "- If not confident or the question is very specific to the context, rely on the provided context to generate your answer.\n"
# #                 "- Summarize the context in simple, clear terms when used.\n"
# #                 "- Cite or reference the context whenever you use information from it.\n"
# #                 "- Maintain a professional, research-oriented tone.\n"
# #             )
# #             if image_paths:
# #                 system_message += (
# #                     f"\nIMPORTANT: The context contains image references. "
# #                     f"After your main response, ask the user: "
# #                     f"'Would you like me to show you the related images from this context?' "
# #                     f"({len(image_paths)} images available).\n"
# #                 )
# #             user_msg = (
# #                 f"{user_input}\n\n"
# #                 f"Relevant research context:\n{context}\n\n"
# #                 f"Please answer the question following the above guidelines."
# #             )
# #             print("\nResearch Mode: Context + knowledge combined response\n")
# #         else:
# #             system_message = (
# #                 "You are a helpful and knowledgeable research assistant.\n"
# #                 "- Provide helpful, accurate, and engaging responses to any question.\n"
# #                 "- Be conversational and adaptive to the user's needs.\n"
# #                 "- If you're unsure about something, be honest about limitations.\n"
# #                 "- Since no specific research context is available, rely on your general knowledge.\n"
# #             )
# #             user_msg = user_input
# #             print("\nGeneral Mode: Generic assistant response\n")

# #         messages = [
# #             {"role": "system", "content": system_message},
# #             {"role": "user", "content": user_msg},
# #         ]

# #         response = llm.invoke(messages)
# #         print("LLM:", response.content)
# #         # return response.content, image_paths


# #     except Exception as e:
# #         print("Error:", e)

# # handle_user_input("what is piechart")

# def is_query_informative(query: str) -> bool:
#     """
#     Returns False for trivial or very short queries.
#     Used to filter out unhelpful user inputs before searching a DB.
#     """
#     if not query or len(query.strip()) < 3:
#         return False
#     trivial_queries = {
#         "hi", "hello", "hey", "test", "ok", "okay", "what's up",
#         "yo", "hmm", "who are you", "yes", "no"
#     }
#     return query.strip().lower() not in trivial_queries




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
#             else:
#                 print("No relevant context found in vector DB.")
#         else:
#             print("Query too generic or informal. Using general assistant mode.")

#         # 2. Detect image paths
#         image_paths = detect_image_paths(context) if context else []

#         # 3. Prepare image descriptions matching image_paths
#         image_contexts = []
#         if chunks and "charts" in chunks:
#             # Try to match charts' image_path with detected image_paths
#             # and extract their context snippet
#             chart_map = {c["image_path"]: c.get("content", "") for c in chunks.get("charts", [])}
#             for img_path in image_paths:
#                 desc = chart_map.get(img_path, "No detailed description available.")
#                 image_contexts.append(desc)
#         else:
#             # If no detailed chunk info, fallback to placeholder descriptions
#             image_contexts = ["Image context not available." for _ in image_paths]

#         # 4. Prepare system message for LLM
#         if context:
#             system_message = (
#                 "You are a highly specialized research assistant.\n"
#                 "- Use the research context provided.\n"
#                 "- Cite context when answering.\n"
#             )
#             if image_paths:
#                 system_message += (
#                     f"Context contains {len(image_paths)} image references.\n"
#                     f"After your answer, ask the user if they want to see the related images."
#                 )
#             user_msg = f"{user_input}\n\nRelevant research context:\n{context}\n\nPlease answer the question."
#         else:
#             system_message = (
#                 "You are a helpful assistant with no extra context."
#             )
#             user_msg = user_input

#         # 5. Prepare messages and call LLM
#         messages = [
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": user_msg},
#         ]
#         response = llm.invoke(messages)

#         # 6. Return assistant text, image paths, image descriptions
#         return response.content, image_paths, image_contexts

#     except Exception as e:
#         print("Error:", e)
#         return "Sorry, something went wrong.", [], []


from llm import get_openai_model
from fetchFromDb import fetch_chunk_from_db
import json
import re
import os

def detect_image_paths(context_text):
    if not context_text:
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
    
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
            match = match.strip('"\'')
            if match and match not in image_paths:
                image_paths.append(match)
    
    return image_paths

def is_query_informative(query: str) -> bool:
    if not query or len(query.strip()) < 3:
        return False
    trivial_queries = {
        "hi", "hello", "hey", "test", "ok", "okay", "what's up",
        "yo", "hmm", "who are you", "yes", "no"
    }
    return query.strip().lower() not in trivial_queries

def summarize_text(llm, text):
    """
    Summarize the input text using the LLM with a concise prompt.
    """
    if not text or len(text.strip()) == 0:
        return "No additional information."
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text clearly and concisely."},
        {"role": "user", "content": f"Summarize the following text clearly and concisely for explaining an image:\n\n{text}"}
    ]
    summary_response = llm.invoke(messages)
    return summary_response.content.strip()

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
            else:
                print("No relevant context found in vector DB.")
        else:
            print("Query too generic or informal. Using general assistant mode.")

        # 2. Detect image paths
        image_paths = detect_image_paths(context) if context else []

        # 3. Prepare image descriptions matching image_paths
        image_contexts_raw = []
        if chunks and "charts" in chunks:
            chart_map = {c["image_path"]: c.get("content", "") for c in chunks.get("charts", [])}
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
            )
            if image_paths:
                system_message += (
                    f"Context contains {len(image_paths)} image references.\n"
                    f"After your answer, ask the user if they want to see the related images."
                )
            user_msg = f"{user_input}\n\nRelevant research context:\n{context}\n\nPlease answer the question."
        else:
            system_message = (
                "You are a helpful assistant with no extra context."
            )
            user_msg = user_input

        # 6. Prepare messages and call LLM for main answer
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_msg},
        ]
        response = llm.invoke(messages)

        # 7. Return assistant text, image paths, and summarized image contexts
        return response.content, image_paths, image_contexts_summarized

    except Exception as e:
        print("Error:", e)
        return "Sorry, something went wrong.", [], []
