import os
from dotenv import load_dotenv

load_dotenv()

# APP ENV
APP_ENV = os.getenv("APP_ENV")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")

# AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "defaultValue")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "defaultValue")
AWS_REGION = os.getenv("AWS_REGION", "defaultValue")

# S3 Bucket (MinIO for dev)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "defaultValue")
S3_BUCKET_NAME = "images"
