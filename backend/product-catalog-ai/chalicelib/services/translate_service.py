import boto3


class TranslateService:
    PLACEHOLDER_TRANSLATIONS = {
        "ko": {
            "Product": "상품",
            "Retail item": "판매 상품",
            "Consumer goods": "소비재",
            "Shoe": "신발",
            "Footwear": "신발류",
            "Fashion accessory": "패션 액세서리",
            "Mobile phone": "휴대전화",
            "Electronics": "전자제품",
            "Gadget": "기기",
            "Bag": "가방",
            "Handbag": "핸드백",
            "Accessory": "액세서리",
        },
        "es": {
            "Product": "producto",
            "Retail item": "articulo minorista",
            "Consumer goods": "bienes de consumo",
            "Shoe": "zapato",
            "Footwear": "calzado",
            "Fashion accessory": "accesorio de moda",
            "Mobile phone": "telefono movil",
            "Electronics": "electronica",
            "Gadget": "dispositivo",
            "Bag": "bolso",
            "Handbag": "bolso de mano",
            "Accessory": "accesorio",
        },
        "fr": {
            "Product": "produit",
            "Retail item": "article de vente",
            "Consumer goods": "biens de consommation",
            "Shoe": "chaussure",
            "Footwear": "chaussures",
            "Fashion accessory": "accessoire de mode",
            "Mobile phone": "telephone portable",
            "Electronics": "electronique",
            "Gadget": "appareil",
            "Bag": "sac",
            "Handbag": "sac a main",
            "Accessory": "accessoire",
        },
    }

    def __init__(self, region: str):
        self.client = boto3.client("translate", region_name=region)

    def translate_labels_placeholder(
        self, labels: list[str], target_languages: list[str]
    ) -> dict[str, list[str]]:
        translations = {}
        for language in target_languages:
            mapping = self.PLACEHOLDER_TRANSLATIONS.get(language, {})
            translations[language] = [mapping.get(label, label) for label in labels]
        return translations

    def translate_labels(
        self, labels: list[str], target_languages: list[str]
    ) -> dict[str, list[str]]:
        translations = {}
        for language in target_languages:
            translated = []
            for label in labels:
                response = self.client.translate_text(
                    Text=label,
                    SourceLanguageCode="en",
                    TargetLanguageCode=language,
                )
                translated.append(response.get("TranslatedText", label))
            translations[language] = translated
        return translations
