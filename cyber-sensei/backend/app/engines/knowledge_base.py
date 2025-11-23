# backend/app/engines/knowledge_base.py
import os
from pathlib import Path
from typing import Dict, Optional

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class PersonalKnowledgeBase:
    def __init__(self, db_path: Optional[str] = None):
        persist_path = Path(db_path or os.getenv("KNOWLEDGE_DB_DIR", "./data/knowledge_db"))
        persist_path.mkdir(parents=True, exist_ok=True)
        self.persist_directory = str(persist_path)
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
        )

    def add_source(self, file_path: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """Loads, chunks, and adds a document to the knowledge base."""
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"

        loader = None
        lower_path = file_path.lower()
        if lower_path.endswith(".txt"):
            loader = TextLoader(file_path)
        elif lower_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            return "Error: Unsupported file type. Please use .txt or .pdf."

        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata = chunk.metadata or {}
            if metadata:
                chunk.metadata.update(metadata)

        self.vector_store.add_documents(chunks)
        self.vector_store.persist()
        return f"Successfully added {os.path.basename(file_path)} to your knowledge base."

    def query(self, query_text: str, k: int = 4) -> str:
        """Queries the knowledge base and returns relevant context."""
        try:
            results = self.vector_store.similarity_search(query_text, k=k)
            if not results:
                return "I couldn't find any relevant information in your personal documents."
            return "\n\n---\n\n".join([doc.page_content for doc in results])
        except Exception as e:
            return f"Error querying knowledge base: {e}"