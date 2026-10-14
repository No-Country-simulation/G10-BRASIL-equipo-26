from fastapi import File, Form, UploadFile
from fastapi.responses import JSONResponse

from src.controller.document_controller import DocumentController

class DocumentResource:
    def __init__(self, document_controller: DocumentController):
        self.document_controller = document_controller
    
    def on_post_documents(
        self,
        title: str = Form(...),
        file: UploadFile = File(...),
    ):
        content = file.file.read()

        result = self.document_controller.create_document(
            title=title,
            filename=file.filename,
            content_type=file.content_type,
            content=content,
        )

        return JSONResponse(
            status_code=202,
            content=result,
        )