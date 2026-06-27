from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_ingest_rejects_non_pdf(client):
    resp = await client.post(
        "/ingest",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


async def test_query_rejects_empty_question(client):
    resp = await client.post("/query", json={"question": ""})
    assert resp.status_code == 400


async def test_query_returns_answer(client):
    mock_result = {
        "answer": "The answer is 42.",
        "sources": [{"filename": "test.pdf", "page": 1, "snippet": "..."}],
    }
    with patch("app.api.query_documents", return_value=mock_result):
        resp = await client.post("/query", json={"question": "What is the answer?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The answer is 42."
    assert len(data["sources"]) == 1


async def test_ingest_success(client):
    mock_result = {"filename": "test.pdf", "chunks": 10, "pages": 3}
    with patch("app.api.ingest_pdf", return_value=mock_result):
        resp = await client.post(
            "/ingest",
            files={"file": ("test.pdf", b"%PDF-fake", "application/pdf")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.pdf"
    assert data["chunks"] == 10
