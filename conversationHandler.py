from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm import get_openai_model

SYSTEM_PROMPT = (
    "You are a highly specialized research assistant. "
    "Use any provided retrieval context when available, but do not invent citations. "
    "If context is insufficient, say so and answer from general knowledge."
)

memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="history",
    input_key="input",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

llm_model = get_openai_model()

conversation = ConversationChain(
    llm=llm_model,
    memory=memory,
    prompt=prompt,
    verbose=False,
)
