import pika
from app import acrcloud_client, spotify_client
import config

def callback(ch, method, properties, body):
    print(f"Received song message: {body}")

    # body will be a file path or base64 data of the song
    with open(body.decode(), "rb") as audio_file:
        audio_data = audio_file.read()

    # Identify song
    song_info = acrcloud_client.identify_song(audio_data)
    print("Song Info:", song_info)

    # Example: get Spotify track_id from song_info
    track_id = song_info['metadata']['music'][0]['external_metadata']['spotify']['track']['id']

    # Get song features
    access_token = spotify_client.get_access_token()
    song_features = spotify_client.get_song_features(track_id, access_token)
    print("Song Features:", song_features)

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=config.RABBITMQ_QUEUE)

    channel.basic_consume(queue=config.RABBITMQ_QUEUE,
                          on_message_callback=callback,
                          auto_ack=True)

    print('Waiting for messages...')
    channel.start_consuming()
