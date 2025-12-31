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
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"

            if not os.path.isfile(file_path):
                return f"Error: Path is not a file: {file_path}"

            loader = None
            lower_path = file_path.lower()
            
            try:
                if lower_path.endswith(".txt") or lower_path.endswith(".md"):
                    loader = TextLoader(file_path, encoding='utf-8')
                elif lower_path.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                else:
                    return f"Error: Unsupported file type. Please use .txt, .md, or .pdf. Got: {Path(file_path).suffix}"

                documents = loader.load()
                if not documents:
                    return f"Error: Could not extract content from {os.path.basename(file_path)}"

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                chunks = text_splitter.split_documents(documents)

                if not chunks:
                    return f"Error: No text chunks created from {os.path.basename(file_path)}"

                for chunk in chunks:
                    chunk.metadata = chunk.metadata or {}
                    if metadata:
                        chunk.metadata.update(metadata)

                self.vector_store.add_documents(chunks)
                self.vector_store.persist()
                
                logger.info(f"Added {len(chunks)} chunks from {os.path.basename(file_path)} to knowledge base")
                return f"Successfully added {os.path.basename(file_path)} ({len(chunks)} chunks) to your knowledge base."
            except Exception as load_error:
                logger.error(f"Error loading document {file_path}: {load_error}")
                return f"Error loading document: {str(load_error)}"
        except Exception as e:
            logger.error(f"Error adding source {file_path}: {e}")
            return f"Error: Failed to add document to knowledge base: {str(e)}"

    def query(self, query_text: str, k: int = 4) -> str:
        """Queries the knowledge base and returns relevant context."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not query_text or len(query_text.strip()) == 0:
            return "Error: Query text is required"
        
        if k < 1 or k > 20:
            k = 4  # Default to 4 if invalid
        
        try:
            results = self.vector_store.similarity_search(query_text.strip(), k=k)
            if not results:
                return "I couldn't find any relevant information in your personal documents."
            
            # Format results with metadata if available
            formatted_results = []
            for i, doc in enumerate(results, 1):
                content = doc.page_content
                meta_info = ""
                if doc.metadata:
                    source = doc.metadata.get('source', '')
                    if source:
                        meta_info = f"\n[Source: {Path(source).name}]"
                formatted_results.append(f"{content}{meta_info}")
            
            return "\n\n---\n\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return f"Error querying knowledge base: {str(e)}"