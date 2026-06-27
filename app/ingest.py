from pathlib import Path

import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def get_embedding_fn() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )


def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_or_create_collection(
    client: chromadb.ClientAPI, name: str = "documents"
) -> chromadb.Collection:
    embedding_fn = get_embedding_fn()

    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=chromadb.utils.embedding_functions.create_langchain_embedding(
            embedding_fn
        ),
    )


def ingest_pdf(file_path: str | Path) -> dict:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = PyPDFLoader(str(file_path))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(pages)

    client = get_chroma_client()
    collection = get_or_create_collection(client)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        doc_id = f"{file_path.stem}_{i}"
        ids.append(doc_id)
        documents.append(chunk.page_content)
        metadatas.append(
            {
                "source": str(file_path.name),
                "page": chunk.metadata.get("page", 0),
            }
        )

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return {
        "filename": file_path.name,
        "chunks": len(chunks),
        "pages": len(pages),
    }
