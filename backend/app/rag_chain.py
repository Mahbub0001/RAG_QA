""" build: retriever -> prompt -> llm -> parser """

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough

from .config import get_settings
from .db import _get_retriever


SYSTEM_PROMPT =(
    "You are a precise assistant. Answers the user's questions only the context provided below."
    "If the context does not contain the answer, say 'I don't know'. Be concise and do not make up answers.\n"
    "Context: \n{context}"
)

_llm = ChatGroq(
    model=get_settings().llm_model,
    api_key=get_settings().groq_api_key,
    temperature=0)

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{question}")
])

def _formate_docs(docs)->str:
    return "\n".join([f"Page {d.metadata['page']}: {d.page_content}" for d in docs])

def _make_sources(docs) -> list[dict]:
    return [
        {
            "page": d.metadata["page"],
            "source": d.metadata["source"],
            "content": d.page_content
        }
        for d in docs
    ]

def ask(question:str, collection:str, k:int=3) -> dict:
    retriever = _get_retriever(collection, k)
    chain=(
        {
            "context": retriever| _formate_docs,
            "question": RunnablePassthrough()
        }
        | _prompt # fill question and context
        | _llm
        | StrOutputParser() # parse llm output to str

    )
    answer = chain.invoke(question)
    docs = retriever.invoke(question)

    return {
        "answer": answer,
        "sources": _make_sources(docs)
    }
