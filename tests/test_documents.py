from fastapi.testclient import TestClient
from src.app import create_app


def test_accepts_markdown_document():
    with TestClient(create_app()) as client:
        response = client.post(
            "/v1/documents",
            data={"title": "Test document"},
            files={"file": ("guide.md", b"# Test document", "text/markdown")},
        )

    assert response.status_code == 202
    assert "document_key" in response.json()