from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from llm import get_openai_model
from fetchFromDb import fetch_chunk_from_db


def handleUserinput():
    try:
        llm = get_openai_model()
        context = fetch_chunk_from_db("boeing")

        prompt = ChatPromptTemplate.from_messages(
            [
                {
                    "role": "system",
                    "content": f"""
                You are a highly knowledgeable research assistant trained to answer questions the research topic provided.

            
                """,
                },
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # user_input = input(")

        user_prompt = f"""
        This is the user's query:

        This is the given user's context.
        --- CONTEXT START ---
        {context if context else "No context provided."}
        --- CONTEXT END ---

        Instructions:
        1. If context is provided and relevant, prioritize it when answering the user's question.
        2. If the context does **not** sufficiently address the question, you may use general, verifiable knowledge to supplement your response — clearly indicate this by saying, "Based on general knowledge, ..."
        3. If no context is available at all, rely on general knowledge, but ensure your answer is appropriate to academic or technical domains.
        4. Always avoid speculation, opinion, or addressing topics completely outside the research or technical scope.
        5. Structure your response clearly, cite which source (context or general knowledge) you're relying on, and ensure accuracy.
        """

        user_message = [{"role": "user", "content": user_input}]

        formatted_prompt = prompt.format_prompt(messages=user_message)
        print("result", formatted_prompt.to_messages)
        response = llm.invoke(formatted_prompt.to_messages())

        print("LLM:", response.content)
    except Exception as e:
        print("Error:", e)


handleUserinput()
