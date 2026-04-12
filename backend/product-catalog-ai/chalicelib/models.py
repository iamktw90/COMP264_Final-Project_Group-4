from dataclasses import dataclass


@dataclass
class AnalysisResult:
    record_id: str
    image_name: str
    labels: list[str]
    translations: dict[str, list[str]]
    image_url: str
    message: str
