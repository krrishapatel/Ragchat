from langchain_ollama import ChatOllama

from app.config import settings
from app.ingest import get_chroma_client, get_or_create_collection

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions "
    "based on the provided context.\n"
    "Use ONLY the context below to answer. If the answer is not "
    "in the context, say \"I don't have enough information to "
    'answer that."\n'
    "Always cite which source document and page number your "
    "answer comes from.\n\n"
    "Context:\n{context}"
)


def query_documents(question: str) -> dict:
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    results = collection.query(
        query_texts=[question],
        n_results=settings.top_k,
    )

    if not results["documents"] or not results["documents"][0]:
        return {
            "answer": "No documents have been ingested yet. Please upload a PDF first.",
            "sources": [],
        }

    context_parts = []
    sources = []

    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        context_parts.append(doc)
        source_info = {
            "filename": metadata.get("source", "unknown"),
            "page": metadata.get("page", 0),
            "snippet": doc[:200],
        }
        if source_info not in sources:
            sources.append(source_info)

    context = "\n\n---\n\n".join(context_parts)

    llm = ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
    )

    messages = [
        ("system", SYSTEM_PROMPT.format(context=context)),
        ("human", question),
    ]

    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "sources": sources,
    }
