from abc import ABC, abstractmethod


class StoragePort(ABC):
    """Port для файлового хранилища (S3/MinIO)."""

    @abstractmethod
    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Загружает байты; возвращает object key."""

    @abstractmethod
    async def delete(self, bucket: str, key: str) -> None:
        """Удаляет объект."""

    @abstractmethod
    def presigned_url(self, bucket: str, key: str, expires_seconds: int = 3600) -> str:
        """Возвращает presigned URL для скачивания."""
