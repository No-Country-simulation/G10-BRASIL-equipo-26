import os

import oci
from fastapi import FastAPI

from src.connectors.oci_object_storage_connector import OCIObjectStorageConnector
from src.controller.document_controller import DocumentController
from src.resources.document import DocumentResource


def create_app(document_controller: DocumentController) -> FastAPI:
    application = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    document_resource = DocumentResource(
        document_controller=document_controller,
    )

    application.add_api_route(
        "/v1/documents",
        document_resource.on_post_documents,
        methods=["POST"],
    )

    return application


def main() -> FastAPI:
    connector = OCIObjectStorageConnector(
        service_endpoint=None,
        namespace_name=os.environ["OCI_OBJECT_STORAGE_NAMESPACE"],
        bucket_name=os.environ["OCI_OBJECT_STORAGE_BUCKET"],
        oci_config=oci.config.from_file(),
    )

    controller = DocumentController(storage_connector=connector)

    return create_app(document_controller=controller)