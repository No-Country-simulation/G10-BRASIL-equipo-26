import pytest

from src.controller.document_controller import DocumentController
from src.errors.document_errors import EmptyDocumentError
from src.errors.document_errors import UnsupportedDocumentFormatError

def test_rejects_empty_document(oci_storage_connector):
    controller = DocumentController(
        storage_connector=oci_storage_connector,
    )

    with pytest.raises(EmptyDocumentError):
        controller.create_document(
            title="Test Document",
            filename="guide.md",
            content_type="text/markdown",
            content=b""
        )

def test_rejects_unsupported_document_extension(oci_storage_connector):
    controller = DocumentController(
        storage_connector=oci_storage_connector,
    )

    with pytest.raises(UnsupportedDocumentFormatError):
        controller.create_document(
            title="Test Document",
            filename="program.exe",
            content_type="text/markdown",
            content=b"non-empty content",
        )

def test_allows_document_extension(oci_storage_connector):
    controller = DocumentController(
        storage_connector=oci_storage_connector,
    )

    controller.create_document(
        title="Test Document",
        filename="guide.md",
        content_type="text/markdown",
        content=b"# Test document",   
    )

def test_document_upload_mockserver(mockserver_upload, oci_storage_connector):
    client, expected_request = mockserver_upload
    controller = DocumentController(
        storage_connector=oci_storage_connector,
    )

    controller.create_document(
        title="Test Document",
        filename="guide.md",
        content_type="text/markdown",
        content=b"# Test document",
    )

    verification = client.put(
        "/mockserver/verify",
        json={
            "httpRequest": expected_request,
            "times": {"atLeast": 1, "atMost": 1},
        },
    )

    assert verification.status_code == 202, verification.text

