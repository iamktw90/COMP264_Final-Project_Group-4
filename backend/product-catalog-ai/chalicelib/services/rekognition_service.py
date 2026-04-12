import boto3


class RekognitionService:
    def __init__(self, region: str):
        self.client = boto3.client("rekognition", region_name=region)

    def detect_labels_placeholder(self, image_name: str) -> list[str]:
        image_name = image_name.lower()
        if "shoe" in image_name:
            return ["Shoe", "Footwear", "Fashion accessory"]
        if "phone" in image_name:
            return ["Mobile phone", "Electronics", "Gadget"]
        if "bag" in image_name:
            return ["Bag", "Handbag", "Accessory"]
        return ["Product", "Retail item", "Consumer goods"]

    def detect_labels(self, bucket_name: str, image_name: str, max_labels: int = 5) -> list[str]:
        response = self.client.detect_labels(
            Image={"S3Object": {"Bucket": bucket_name, "Name": image_name}},
            MaxLabels=max_labels,
            MinConfidence=70,
        )
        labels = [item["Name"] for item in response.get("Labels", [])]
        return labels or self.detect_labels_placeholder(image_name)
