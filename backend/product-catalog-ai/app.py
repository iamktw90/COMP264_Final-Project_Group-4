from chalice import BadRequestError, Chalice, Response

from chalicelib.config import AppConfig
from chalicelib.services.catalog_service import CatalogService

app = Chalice(app_name="product-catalog-ai")
app.debug = True

config = AppConfig.from_env()
catalog_service = CatalogService(config=config)


@app.route("/", methods=["GET"], cors=True)
def index():
    return {
        "message": "Product Catalog AI backend is running.",
        "service": app.app_name,
    }


@app.route("/health", methods=["GET"], cors=True)
def health():
    return {
        "status": "ok",
        "service": app.app_name,
        "aws_ready": config.is_aws_ready,
    }


@app.route("/config", methods=["GET"], cors=True)
def get_config_status():
    return {
        "bucket_configured": bool(config.s3_bucket_name),
        "table_configured": bool(config.dynamodb_table_name),
        "region": config.aws_region,
        "languages": config.target_languages,
    }


@app.route("/analyze", methods=["POST"], cors=True)
def analyze_product():
    request = app.current_request
    payload = request.json_body or {}
    image_name = payload.get("image_name")

    if not image_name:
        raise BadRequestError("The 'image_name' field is required.")

    result = catalog_service.analyze_placeholder(image_name=image_name)
    return Response(body=result, status_code=200)


@app.route("/upload", methods=["POST"], cors=True)
def upload_product():
    request = app.current_request
    payload = request.json_body or {}
    image_name = (payload.get("image_name") or "").strip()
    image_base64 = payload.get("image_base64")

    if not image_name:
        raise BadRequestError("The 'image_name' field is required.")

    if not image_base64:
        raise BadRequestError("The 'image_base64' field is required.")

    result = catalog_service.process_uploaded_image(
        image_name=image_name,
        image_base64=image_base64,
    )
    return Response(body=result, status_code=200)


@app.route("/results", methods=["GET"], cors=True)
def list_results():
    items = catalog_service.list_results()
    return {"items": items, "count": len(items)}


@app.route("/results/{record_id}", methods=["GET"], cors=True)
def get_result(record_id: str):
    result = catalog_service.get_result(record_id)
    if not result:
        return Response(
            body={"error": "Result not found."},
            status_code=404,
        )
    return result
