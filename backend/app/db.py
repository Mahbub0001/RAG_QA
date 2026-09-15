import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from .embedding import get_embedding

INDEX_DIR = Path(os.environ.get("FAISS_INDEX_DIR", "./.faiss_index"))

def _path(collection: str) -> Path:
    return INDEX_DIR / collection

def _load(collection:str) -> FAISS|None:
    path = _path(collection)
    if path.exists():
        return FAISS.load_local(
            str(path),
            get_embedding(),
            allow_dangerous_deserialization=True
        )
    return None

def _save(collection:str, store: FAISS) -> None:
    path = _path(collection)
    path.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path))  #write index.fiass + pickle to sidecar file

def _get_retriever(collection:str, k:int):
    store = _load(collection)
    if store is None:
        raise ValueError(f"Collection '{collection}' does not exist.")
    return store.as_retriever(search_kwargs={"k": k})

def add_documents_to_collection(collection:str, documents) -> None:
    store = _load(collection)
    if store is None:
        store = FAISS.from_documents(documents, embedding=get_embedding())
    else:
        store.add_documents(documents)
    _save(collection, store)