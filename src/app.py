from fastapi import FastAPI
from src.resources.document import DocumentResource

def create_app() -> FastAPI:
    application = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    document_resource = DocumentResource()

    application.add_api_route(
        "/v1/documents", document_resource.on_post_documents, methods=["POST"],
    )
    
    return application

def main() -> FastAPI:

    return create_app()


app = main()