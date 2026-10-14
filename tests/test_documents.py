from fastapi.testclient import TestClient

from src.app import create_app
from src.controller.document_controller import DocumentController


def test_accepts_markdown_document(
    oci_storage_connector,
    mockserver_upload,
):
    mockserver_client, expected_request = mockserver_upload

    controller = DocumentController(
        storage_connector=oci_storage_connector,
    )
    application = create_app(document_controller=controller)

    with TestClient(application) as client:
        response = client.post(
            "/v1/documents",
            data={"title": "Test document"},
            files={
                "file": (
                    "guide.md", 
                    b"# Test document", 
                    "text/markdown"
                )
            },
        )

    assert response.status_code == 202
    assert "document_key" in response.json()

    verification = mockserver_client.put(
        "/mockserver/verify",
        json={
            "httpRequest": expected_request,
            "times": {"atLeast": 1, "atMost": 1},
        },
    )

    assert verification.status_code == 202, verification.text