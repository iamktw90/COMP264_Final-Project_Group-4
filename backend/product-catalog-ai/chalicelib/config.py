import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""
    dynamodb_table_name: str = ""
    target_languages: list[str] = field(
        default_factory=lambda: ["ko", "es", "fr"]
    )

    @property
    def is_aws_ready(self) -> bool:
        return bool(self.s3_bucket_name and self.dynamodb_table_name)

    @classmethod
    def from_env(cls) -> "AppConfig":
        raw_languages = os.getenv("TARGET_LANGUAGES", "ko,es,fr")
        languages = [item.strip() for item in raw_languages.split(",") if item.strip()]
        return cls(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            s3_bucket_name=os.getenv("S3_BUCKET_NAME", ""),
            dynamodb_table_name=os.getenv("DYNAMODB_TABLE_NAME", ""),
            target_languages=languages or ["ko", "es", "fr"],
        )
