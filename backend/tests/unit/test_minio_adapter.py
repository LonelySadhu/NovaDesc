"""Unit tests for MinioAdapter."""
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.storage.minio_adapter import MinioAdapter


@pytest.fixture
def mock_minio_client():
    with patch("infrastructure.storage.minio_adapter.Minio") as MockMinio:
        client = MagicMock()
        MockMinio.return_value = client
        adapter = MinioAdapter(
            endpoint="localhost:9000",
            access_key="key",
            secret_key="secret",
            secure=False,
        )
        yield adapter, client


@pytest.mark.asyncio
async def test_upload_creates_bucket_if_missing(mock_minio_client):
    adapter, client = mock_minio_client
    client.bucket_exists.return_value = False

    key = await adapter.upload("my-bucket", "path/file.jpg", b"data", "image/jpeg")

    client.make_bucket.assert_called_once_with("my-bucket")
    client.put_object.assert_called_once()
    assert key == "path/file.jpg"


@pytest.mark.asyncio
async def test_upload_skips_bucket_creation_if_exists(mock_minio_client):
    adapter, client = mock_minio_client
    client.bucket_exists.return_value = True

    await adapter.upload("my-bucket", "path/file.jpg", b"data", "image/jpeg")

    client.make_bucket.assert_not_called()
    client.put_object.assert_called_once()


@pytest.mark.asyncio
async def test_upload_passes_content_type(mock_minio_client):
    adapter, client = mock_minio_client
    client.bucket_exists.return_value = True

    await adapter.upload("bucket", "doc.pdf", b"pdf-bytes", "application/pdf")

    _, kwargs = client.put_object.call_args
    assert kwargs.get("content_type") == "application/pdf"


@pytest.mark.asyncio
async def test_delete_calls_remove_object(mock_minio_client):
    adapter, client = mock_minio_client

    await adapter.delete("bucket", "path/file.jpg")

    client.remove_object.assert_called_once_with("bucket", "path/file.jpg")


@pytest.mark.asyncio
async def test_delete_ignores_s3_error(mock_minio_client):
    from minio.error import S3Error
    adapter, client = mock_minio_client
    client.remove_object.side_effect = S3Error(
        "NoSuchKey", "key not found", "resource", "request_id", "host_id", MagicMock()
    )

    # должно пройти без исключения
    await adapter.delete("bucket", "missing-key")


def test_presigned_url_returns_client_result(mock_minio_client):
    adapter, client = mock_minio_client
    client.presigned_get_object.return_value = "http://minio/bucket/key?sig=abc"

    url = adapter.presigned_url("bucket", "path/file.jpg", expires_seconds=600)

    assert url == "http://minio/bucket/key?sig=abc"
    client.presigned_get_object.assert_called_once()
