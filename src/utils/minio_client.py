"""
Minio client.

Author  : Coke
Date    : 2025-04-03
"""

from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from src.schemas.base import BaseModel

KB = 1024
MB = KB * KB
GB = MB * KB
TB = GB * KB


class UploadPart(BaseModel):
    part_number: str
    upload_id: str


class MinioClient:
    # TODO: undone.
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        *,
        bucket_name: str | None = None,
        secure: bool = False,
    ):
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket_name = bucket_name
        self._client = Minio(
            self._endpoint,
            access_key=self._access_key,
            secret_key=self._secret_key,
            secure=secure,
        )

    @property
    def client(self) -> Minio:
        return self._client

    @property
    def bucket_name(self) -> str:
        if self._bucket_name is None:
            raise AttributeError("Bucket name is not set.")

        if not self.bucket_exists(self._bucket_name):
            raise AttributeError(f"Bucket does not exist: {self._bucket_name}")

        return self._bucket_name

    def bucket_exists(self, bucket_name: str) -> bool:
        return self.client.bucket_exists(bucket_name)

    def file_exists(self, filename: str, *, bucket_name: str | None = None, nullable: bool = True) -> bool:
        bucket_name = bucket_name or self.bucket_name

        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=filename)
            return True
        except S3Error:
            if not nullable:
                raise
            return False

    def presigned_get_url(
        self,
        filename: str,
        *,
        bucket_name: str | None = None,
        nullable: bool = True,
        expires: timedelta = timedelta(days=30),
    ) -> str:
        bucket_name = bucket_name or self.bucket_name
        if not nullable:
            self.file_exists(filename, bucket_name=bucket_name, nullable=False)
        return self.client.presigned_get_object(bucket_name=bucket_name, object_name=filename, expires=expires)

    def create_multipart_upload(
        self,
        filename: str,
        *,
        bucket_name: str | None = None,
        headers: dict | None = None,
    ) -> str:
        bucket_name = bucket_name or self.bucket_name
        headers = headers or {}
        return self.client._create_multipart_upload(bucket_name=bucket_name, object_name=filename, headers=headers)

    def complete_multipart_upload(
        self,
        filename: str,
        upload_id: str,
        max_parts: int,
        *,
        bucket_name: str | None = None,
    ) -> None:
        bucket_name = bucket_name or self.bucket_name
        part_list = self.client._list_parts(
            bucket_name=bucket_name,
            object_name=filename,
            upload_id=upload_id,
            max_parts=max_parts,
        )
        self.client._complete_multipart_upload(
            bucket_name=bucket_name,
            object_name=filename,
            upload_id=upload_id,
            parts=part_list.parts,
        )

    def presigned_put_url(
        self,
        filename: str,
        *,
        bucket_name: str | None = None,
        upload_part: UploadPart | dict[str, str] | None = None,
        expires: timedelta = timedelta(days=2),
    ) -> str:
        bucket_name = bucket_name or self.bucket_name
        upload_part_map = {}
        if upload_part is not None:
            if isinstance(upload_part, dict):
                upload_part = UploadPart.model_validate(upload_part)

            if int(upload_part.part_number) < 1:
                raise AttributeError(f"Invalid part number: {upload_part.part_number}")

            upload_part_map = upload_part.serializable_dict()

        return self.client.get_presigned_url(
            "PUT",
            bucket_name,
            filename,
            expires=expires,
            extra_query_params=upload_part_map,
        )


if __name__ == "__main__":
    _endpoint = "localhost:9000"
    _access_key = "NkrNxZ6xgBPwNJQKLC1D"
    _secret_key = "9CE45VMwSd6DcHvVijQGj3fwSkX0uMOcbwxgs1Ue"
    _bucket_name = "test-bucket"
    client = MinioClient(_endpoint, access_key=_access_key, secret_key=_secret_key, bucket_name=_bucket_name)
    print(client.presigned_put_url("123", upload_part={"part_number": "1", "upload_id": "123"}))
