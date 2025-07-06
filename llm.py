from langchain_openai import ChatOpenAI
from utils import get_env_variable

def get_openai_model() -> ChatOpenAI:
    """
    Returns a LangChain OpenAI LLM instance.
    """
    api_key = get_env_variable("OPENAI_API_KEY")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)