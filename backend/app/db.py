import os
from pathlib import Path

from .embedding import get_embedding

INDEX_DIR = Path(os.environ.get("FAISS_INDEX_DIR", "./.faiss_index"))