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
