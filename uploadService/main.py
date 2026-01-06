from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import json
from s3_utils import ImageBucket
from msgBroker_Interface import MessageBroker
from config import APP_ENV, LOGGING_LEVEL
from rabbitmq import RabbitMQ
import asyncio
import time
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

    # Temporarily share same both in prod and dev mode -> Later separate type of tech based on env mode (S3/MinIO)
    app.state.imgBucket = ImageBucket()
    
    if APP_ENV == "prod":
        # Initiate SQS
        app.state.broker: MessageBroker = SQS()

        app.state.logger.info("UploadService is in PRODUCTION mode: using SQS")
    elif APP_ENV == "dev":
        # Initiate RabbitMQ
        app.state.broker: MessageBroker = RabbitMQ("UploadService") 
        await app.state.broker.connect() # Asynchronous connect app to RabbitMQ server
        asyncio.create_task(consume_messages()) # Run a concurrent background loop to fetch message from RabbitMQ 

        app.state.logger.info("UploadService is in DEVELOPMENT mode: using RabbitMQ, MinIO")

@app.on_event("shutdown")
async def shutdown_event():
    if APP_ENV == "dev":
        await app.state.broker.close()

############################
# Main Service
############################
@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    x_user_id: str = Header(...),
    x_user_roles: str | None = Header(None),
):
    try:
        try:
            image_data = await file.read()
        except Exception as e:
            raise FileReadError("Failed to read image") from e
        
        # Store to s3
        image_key = f"users/{x_user_id}/images/{image_id}_{file.filename}"
        app.state.imgBucket.upload_image_to_s3(key=image_key, data=image_data, contentType=file.content_type)

    except Exception as e:
        app.state.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-song")
async def upload_song(
    file: UploadFile = File(...),
    x_user_id: str = Header(...),
):
    try: 
        try:
            song_data = await file.read()
        except Exception as e:
            app.state.logger.error(f"Failed to read song: {e}")
            raise FileReadError("Failed to read song") from e

            # Push to RabbitMQ
        await app.state.broker.send(userID=x_user_id, audio_data=song_data, fileName=file.filename, contentType=file.content_type)
    except Exception as e:
        app.state.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


############################
# Test RabbitMQ
############################
async def consume_messages():
    while True:
        msg = await app.state.broker.get() # Return a dict
        if msg:
            app.state.logger.info(f"UploadService received status of {msg['fileName']} from user {msg['userID']}")
        await asyncio.sleep(0.01)

# @app.get("/sse")
# async def sse_endpoint(userID: str):
#     return StreamingResponse(consume_messages(), media_type="text/event-stream")

# Implement SSE connection to push noti back to correct user when receive noti from rabbitMQ