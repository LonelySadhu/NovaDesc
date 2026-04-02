import asyncio
import io
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from domain.storage.ports import StoragePort


class MinioAdapter(StoragePort):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
    ) -> None:
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        def _sync() -> str:
            self._ensure_bucket(bucket)
            self._client.put_object(
                bucket,
                key,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            return key

        return await asyncio.to_thread(_sync)

    async def delete(self, bucket: str, key: str) -> None:
        def _sync() -> None:
            try:
                self._client.remove_object(bucket, key)
            except S3Error:
                pass

        await asyncio.to_thread(_sync)

    def presigned_url(self, bucket: str, key: str, expires_seconds: int = 3600) -> str:
        return self._client.presigned_get_object(
            bucket,
            key,
            expires=timedelta(seconds=expires_seconds),
        )