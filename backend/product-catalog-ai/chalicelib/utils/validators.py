from pathlib import Path


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_image_name(image_name: str) -> None:
    if not image_name or not image_name.strip():
        raise ValueError("Image name cannot be empty.")

    suffix = Path(image_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file format. Please use JPG, JPEG, or PNG.")
