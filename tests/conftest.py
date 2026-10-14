import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from src.connectors.oci_object_storage_connector import OCIObjectStorageConnector

import httpx
import pytest


@pytest.fixture
def mockserver_upload():
    expectation_file = (
        Path(__file__).parent
        / "mockserver"
        / "upload_document_success.json"
    )
    expectation = json.loads(
        expectation_file.read_text(encoding="utf-8")
    )

    with httpx.Client(
        base_url="http://localhost:1080",
        timeout=5,
        trust_env=False,
    ) as client:
        client.put("/mockserver/reset").raise_for_status()
        client.put(
            "/mockserver/expectation",
            json=expectation,
        ).raise_for_status()

        yield client, expectation["httpRequest"]

        client.put("/mockserver/reset").raise_for_status()

@pytest.fixture
def oci_test_config():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    key_content = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    return {
        "user": "ocid1.user.oc1..testuser",
        "tenancy": "ocid1.tenancy.oc1..testtenancy",
        "fingerprint": "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
        "region": "us-ashburn-1",
        "key_content": key_content,
    }

@pytest.fixture
def oci_storage_connector(mockserver_upload, oci_test_config):
    mockserver_client, _ = mockserver_upload

    connector = OCIObjectStorageConnector(
        service_endpoint=str(mockserver_client.base_url).rstrip("/"),
        namespace_name="test-namespace",
        bucket_name="test-documents",
        oci_config=oci_test_config,
    )

    connector.client.base_client.session.trust_env = False

    yield connector

    connector.client.base_client.session.close()