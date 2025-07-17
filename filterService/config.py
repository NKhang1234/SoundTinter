import os
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "defaultValue")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "defaultValue")
AWS_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "defaultValue")
AWS_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "defaultValue")
S3_REGION = os.getenv("S3_REGION", "defaultValue")
