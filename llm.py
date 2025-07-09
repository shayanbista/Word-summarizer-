from langchain_openai import ChatOpenAI
from utils import get_env_variable


def get_openai_model() -> ChatOpenAI:
    """
    Returns a LangChain OpenAI LLM instance.
    """
    api_key = get_env_variable("API_KEY")
    return ChatOpenAI(model="gpt-4.1-nano", temperature=0.7, openai_api_key=api_key)
