from fastapi import File, Form, UploadFile

class DocumentResource:
    def on_post_documents(
            self,
            title: str = Form(...),
            file: UploadFile = File(...),
        ):
            pass