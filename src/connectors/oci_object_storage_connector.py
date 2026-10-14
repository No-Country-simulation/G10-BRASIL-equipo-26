import oci

class OCIObjectStorageConnector:
    def __init__(
            self,
            service_endpoint: str | None,
            namespace_name: str,
            bucket_name:str,
            oci_config: dict,
    ):
            self.service_endpoint = service_endpoint
            self.namespace_name = namespace_name
            self.bucket_name = bucket_name

            self.client = oci.object_storage.ObjectStorageClient(
                   config=oci_config,
                   service_endpoint=self.service_endpoint,
                   timeout=5,
                   retry_strategy=oci.retry.NoneRetryStrategy(),
            )

    def upload_document(
            self,
            filename: str,
            content_type: str,
            content: bytes,
    ):
            return self.client.put_object(
               namespace_name=self.namespace_name,
               bucket_name=self.bucket_name,
               object_name=filename,
               content_type=content_type,
               put_object_body=content,
            )