from unittest.mock import MagicMock, patch

import pytest

from app.ingest import ingest_pdf


def test_ingest_file_not_found():
    with pytest.raises(FileNotFoundError):
        ingest_pdf("/nonexistent/path.pdf")


@patch("app.ingest.get_or_create_collection")
@patch("app.ingest.get_chroma_client")
@patch("app.ingest.PyPDFLoader")
def test_ingest_pdf_success(mock_loader_cls, mock_client, mock_collection, tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    mock_doc = MagicMock()
    mock_doc.page_content = "Hello world " * 50
    mock_doc.metadata = {"page": 0}

    mock_loader = MagicMock()
    mock_loader.load.return_value = [mock_doc]
    mock_loader_cls.return_value = mock_loader

    mock_col = MagicMock()
    mock_collection.return_value = mock_col

    result = ingest_pdf(pdf_path)

    assert result["filename"] == "test.pdf"
    assert result["pages"] == 1
    assert result["chunks"] >= 1
    mock_col.add.assert_called_once()
