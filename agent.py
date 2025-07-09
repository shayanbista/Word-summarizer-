from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from llm import get_openai_model
from fetchFromDb import fetch_chunk_from_db

def needs_context(query: str) -> bool:
    research_keywords = [
        "research", "analyze", "analysis", "report on",
        "look into", "dive into", "explore", "investigate"
    ]
    domain_keywords = ["industry", "supply chain", "market", "business model", "company", "startup"]

    query_lower = query.lower()
    return any(k in query_lower for k in research_keywords + domain_keywords)

def handle_user_input():
    try:
        llm = get_openai_model()
        user_input = input("You: ").strip()
        use_context = needs_context(user_input)
        context = fetch_chunk_from_db(user_input) if use_context else None

        system_message = (
            "You are a highly specialized research assistant.\n"
            "- Only respond to research-related or analytical questions.\n"
            "- If the query is casual, general, or non-research, say: 'I'm designed to assist only with research-related questions.'\n"
            "- If context is provided, prioritize it.\n"
            "- If context is not available, say so clearly but answer based on general domain knowledge.\n"
            "- Never speculate or give personal opinions.\n"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="messages"),
                ("system", system_message),
            ]
        )

        if context:
            user_msg = f"{user_input}\n\nHere is some background information to help you:\n{context}"
        else:
            user_msg = user_input

        messages = [{"role": "user", "content": user_msg}]
        formatted_prompt = prompt.format_prompt(messages=messages)
        response = llm.invoke(formatted_prompt.to_messages())

        print("\nLLM:", response.content)

    except Exception as e:
        print("Error:", e)

handle_user_input()
