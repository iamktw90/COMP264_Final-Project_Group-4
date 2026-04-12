from binascii import Error as BinasciiError
from botocore.exceptions import BotoCoreError, ClientError

from chalicelib.config import AppConfig
from chalicelib.services.dynamodb_service import DynamoDBService
from chalicelib.services.rekognition_service import RekognitionService
from chalicelib.services.s3_service import S3Service
from chalicelib.services.translate_service import TranslateService


class CatalogService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.s3_service = S3Service(
            bucket_name=config.s3_bucket_name,
            region=config.aws_region,
        )
        self.rekognition_service = RekognitionService(region=config.aws_region)
        self.translate_service = TranslateService(region=config.aws_region)
        self.dynamodb_service = DynamoDBService(
            table_name=config.dynamodb_table_name,
            region=config.aws_region,
        )
        self._placeholder_results: list[dict] = []

    def analyze_placeholder(self, image_name: str) -> dict:
        labels = self.rekognition_service.detect_labels_placeholder(image_name)
        return self._build_result(
            image_name=image_name,
            labels=labels,
            message="Placeholder analysis completed. Replace with real AWS calls next.",
        )

    def process_uploaded_image(self, image_name: str, image_base64: str) -> dict:
        try:
            image_bytes = self.s3_service.decode_image_placeholder(image_base64)
            content_type = self.s3_service.infer_content_type(image_name)
        except (ValueError, BinasciiError) as error:
            raise ValueError(str(error)) from error

        if len(image_bytes) == 0:
            raise ValueError("Uploaded image is empty.")

        if not self.config.is_aws_ready:
            labels = self.rekognition_service.detect_labels_placeholder(image_name)
            return self._build_result(
                image_name=image_name,
                labels=labels,
                message="Upload processed locally with placeholder AI flow.",
                extra={
                    "content_type": content_type,
                    "image_size_bytes": len(image_bytes),
                    "storage_mode": "placeholder",
                },
            )

        try:
            image_url = self.s3_service.upload_image(
                image_name=image_name,
                image_bytes=image_bytes,
                content_type=content_type,
            )
            labels = self.rekognition_service.detect_labels(
                bucket_name=self.config.s3_bucket_name,
                image_name=image_name,
            )
            translations = self.translate_service.translate_labels(
                labels=labels,
                target_languages=self.config.target_languages,
            )
            record = self.dynamodb_service.build_placeholder_record(
                image_name=image_name,
                image_url=image_url,
                labels=labels,
                translations=translations,
            )
            self.dynamodb_service.save_record(record)
            payload = {
                **record,
                "message": "Upload processed with AWS services.",
                "content_type": content_type,
                "image_size_bytes": len(image_bytes),
                "storage_mode": "aws",
            }
            self._placeholder_results.append(payload)
            return payload
        except (BotoCoreError, ClientError) as error:
            labels = self.rekognition_service.detect_labels_placeholder(image_name)
            return self._build_result(
                image_name=image_name,
                labels=labels,
                message=f"AWS processing failed, fallback placeholder used: {error}",
                extra={
                    "content_type": content_type,
                    "image_size_bytes": len(image_bytes),
                    "storage_mode": "fallback",
                },
            )

    def list_placeholder_results(self) -> list[dict]:
        return list(reversed(self._placeholder_results))

    def list_results(self) -> list[dict]:
        if self.config.is_aws_ready:
            try:
                records = self.dynamodb_service.list_records()
                if records:
                    return records
            except (BotoCoreError, ClientError):
                pass
        return self.list_placeholder_results()

    def get_result(self, record_id: str) -> dict | None:
        if self.config.is_aws_ready:
            try:
                record = self.dynamodb_service.get_record(record_id)
                if record:
                    return record
            except (BotoCoreError, ClientError):
                pass
        for item in self._placeholder_results:
            if item.get("record_id") == record_id:
                return item
        return None

    def _build_result(
        self,
        image_name: str,
        labels: list[str],
        message: str,
        extra: dict | None = None,
    ) -> dict:
        translations = self.translate_service.translate_labels_placeholder(
            labels=labels,
            target_languages=self.config.target_languages,
        )
        image_url = self.s3_service.build_image_url(
            image_name=image_name,
            region=self.config.aws_region,
        )
        record = self.dynamodb_service.build_placeholder_record(
            image_name=image_name,
            image_url=image_url,
            labels=labels,
            translations=translations,
        )
        payload = {**record, "message": message}
        if extra:
            payload.update(extra)
        self._placeholder_results.append(payload)
        return payload
