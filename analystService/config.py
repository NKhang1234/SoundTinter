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

# AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "defaultValue")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# S3 Bucket (MinIO for dev)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_BUCKET_NAME = "songs"

# DynamoDB
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")
DYNAMODB_TABLE_NAME = "featureSongs"
DYNAMODB_PARTITION_KEY = "userID"
DYNAMODB_SORT_KEY = "songName"
