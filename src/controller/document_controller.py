from pathlib import Path

from src.errors.document_errors import EmptyDocumentError
from src.errors.document_errors import UnsupportedDocumentFormatError
from src.connectors.oci_object_storage_connector import OCIObjectStorageConnector

class DocumentController:
    def __init__(self, storage_connector: OCIObjectStorageConnector):
        self.storage_connector = storage_connector
    
    def create_document(
            self,
            title: str,
            filename: str,
            content_type: str,
            content: bytes,
    ):
        if not content:
            raise EmptyDocumentError(
                "Document content cannot be empty."
            )
        
        extension = Path(filename).suffix.lower()
        if extension not in {".pdf", ".txt", ".md"}:
            raise UnsupportedDocumentFormatError(
                "Document format type is not supported."
            )

        self.storage_connector.upload_document(
            filename=filename,
            content_type=content_type,
            content=content,
        )
        
        return {
            "document_key": filename,
        }