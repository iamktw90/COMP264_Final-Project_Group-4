# Product Catalog AI Backend

## Purpose

This backend is designed for the COMP264 final project using AWS Chalice.

## Current State

The current implementation is a scaffold that includes:

1. Health and configuration endpoints
2. A placeholder analysis endpoint
3. A local upload endpoint using base64 image content
4. Real AWS-ready service modules for S3, Rekognition, Translate, and DynamoDB
5. Placeholder fallback behavior for local debugging

## Endpoints

- `GET /`
- `GET /health`
- `GET /config`
- `POST /analyze`
- `POST /upload`
- `GET /results`
- `GET /results/{record_id}`

## Example Request

```json
{
  "image_name": "shoe-sample.jpg"
}
```

## Example Upload Request

```json
{
  "image_name": "shoe-sample.jpg",
  "image_base64": "BASE64_IMAGE_CONTENT"
}
```

## Local Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chalice local
```

## Next Backend Tasks

1. Test live S3 upload from the frontend.
2. Verify Rekognition labels on real product images.
3. Verify Translate outputs for Korean, Spanish, and French.
4. Improve frontend result rendering and record browsing.
5. Add stricter file validation and deployment settings.
