import os
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "songs_queue")

# ACRCloud
ACRCLOUD_HOST = os.getenv("ACRCLOUD_HOST")
ACRCLOUD_KEY = os.getenv("ACRCLOUD_KEY")
ACRCLOUD_SECRET = os.getenv("ACRCLOUD_SECRET")

# Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# S3 Bucket (MinIO for dev)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "defaultValue")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME_SONGS", "defaultValue")
AWS_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "defaultValue")
AWS_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "defaultValue")
S3_REGION = os.getenv("S3_REGION", "defaultValue")
