import base64
from pathlib import Path

import boto3


class S3Service:
    def __init__(self, bucket_name: str, region: str):
        self.bucket_name = bucket_name
        self.region = region
        self.client = boto3.client("s3", region_name=region)

    def build_image_url(self, image_name: str, region: str) -> str:
        if not self.bucket_name:
            return ""
        return (
            f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{image_name}"
        )

    def decode_image_placeholder(self, image_base64: str) -> bytes:
        return base64.b64decode(image_base64)

    def infer_content_type(self, image_name: str) -> str:
        suffix = Path(image_name).suffix.lower()
        if suffix == ".png":
            return "image/png"
        if suffix in {".jpg", ".jpeg"}:
            return "image/jpeg"
        raise ValueError("Unsupported file format. Please use JPG, JPEG, or PNG.")

    def upload_image(self, image_name: str, image_bytes: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=image_name,
            Body=image_bytes,
            ContentType=content_type,
        )
        return self.build_image_url(image_name=image_name, region=self.region)
