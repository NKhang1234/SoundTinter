from fastapi import FastAPI, UploadFile, File, HTTPException
from essentiaWrapper import EssentiaExtractor
import json
from exceptions import FileReadError
from s3_utils import SongBucket
from dynamoDB_utils import FeatureDynamo
from config import APP_ENV, LOGGING_LEVEL, DYNAMODB_PARTITION_KEY, DYNAMODB_SORT_KEY
from rabbitmq import RabbitMQ
import asyncio
import logging

app = FastAPI()

############################
# Start_up & Shut_down event
############################
@app.on_event("startup")
async def startup_event():
    ###################################################################
    # Set up Logging
    ###################################################################
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    logLevel = level_map.get(LOGGING_LEVEL.lower(), logging.INFO)

    logging.basicConfig(
        level=logLevel,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app.state.logger = logging.getLogger(__name__)

    ###################################################################
    # Set up Environment
    ###################################################################

    # Temporarily share same both in prod and dev mode -> Later separate type of tech based on env mode (S3/MinIO - Dynamo Local/Dynamo Cloud)
    app.state.extractor = EssentiaExtractor()
    app.state.songBucket = SongBucket()
    app.state.featDyna = FeatureDynamo()

    if APP_ENV == "prod":
        app.state.logger.info("AnalystService is in PRODUCTION mode")
    elif APP_ENV == "dev":
        # Initiate RabbitMQ
        app.state.broker: MessageBroker = RabbitMQ("AnalystService")
        await app.state.broker.connect() # Asynchronous connect app to RabbitMQ server
        asyncio.create_task(consume_messages()) # Run a concurrent background loop to fetch message from RabbitMQ 

        app.state.logger.info("AnalystService is in DEVELOPMENT mode")

@app.on_event("shutdown")
async def shutdown_event():
    if APP_ENV == "dev":
        await app.state.broker.close()


############################
# HTTP API for test
############################
@app.post("/test/analyze-song")
async def analyze_song(file: UploadFile = File(...)):
    try:
        try:
            audio_data = await file.read()
        except Exception as e:
            raise FileReadError("Failed to read audio") from e

        if app.state.songBucket.check_if_exist(fileName=file.filename):
            raise FileExistsError(f"{file.filename} already exists in bucket")

        msg = {
            "userID": 'user1', # Temporaly hardcode user1
            "audio_data": audio_data,
            "fileName": file.filename,
            "contentType": file.content_type
        }
        features = analyze_song(msg)

        return features

    except Exception as e:
        app.state.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

############################
# Main Service
############################
async def consume_messages():
    while True:
        msg = await app.state.broker.get() # Return a dict
        if msg:
            app.state.logger.info(f"AnalystService received: {msg['fileName']} from user {msg['userID']}")
            await analyze_song(msg)
        await asyncio.sleep(0.01)

async def analyze_song(msg: dict) -> dict:
    try:
        # Extract features
        features = app.state.extractor.extract_from_bytes(msg["audio_data"])

        # Store features to DynamoDB
        features[DYNAMODB_PARTITION_KEY] = msg["userID"]
        features[DYNAMODB_SORT_KEY] = msg["fileName"]
        app.state.featDyna.add_item(features)

        # Store songs to S3
        app.state.songBucket.upload_song_to_s3(
            fileName=msg["fileName"], 
            data=msg["audio_data"], 
            contentType=msg["contentType"]
        )
    except Exception as e:
        app.state.logger.error(f"Failed to analyse song | userID:{msg['userID']} - {msg['fileName']} with error {e}")
        raise
    else:
        await app.state.broker.send(msg['userID'], msg['fileName'], status='Finish')

    # return features

@app.get("/")
def root():
    return {"message": "Song Analyst Service is running"}
