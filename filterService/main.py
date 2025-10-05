from fastapi import FastAPI, Query, Response, HTTPException
import numpy as np
import cv2
from s3_utils import ImageBucket
from filters import FILTER_MAP
from config import APP_ENV, LOGGING_LEVEL
import logging
import asyncio
from rabbitmq import RabbitMQ
from msgBroker_Interface import MessageBroker

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
        app.state.logger.info("FilterService is in PRODUCTION mode")
    elif APP_ENV == "dev":
        # Initiate RabbitMQ
        app.state.broker: MessageBroker = RabbitMQ("FilterService")
        await app.state.broker.connect() # Asynchronous connect app to RabbitMQ server
        # asyncio.create_task(consume_messages()) # Run a concurrent background loop to fetch message from RabbitMQ 

        app.state.logger.info("FilterService is in DEVELOPMENT mode")
@app.on_event("shutdown")
async def shutdown_event():
    if APP_ENV == "dev":
        await app.state.broker.close()

############################
# HTTP API for test
############################  
@app.post("/test/request_filter")
async def request_filter(songName: str = Query(...), imageID: str = Query(...)):
    try: 
        try:
            # Temporaly hardcode userID = "user1"
            userID = "user1"
            await app.state.broker.send(userID=userID, songName=songName)
        except Exception as e:
            app.state.logger.error(f"Failed to send mapping request to MappingService| song name: {songName}, user: {userID}")

        timeout = 5
        start = asyncio.get_event_loop().time()
        msg = None
        while True:
            msg = await app.state.broker.get()
            if msg:
                break
            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError("No message received from MappingService within timeout")
            await asyncio.sleep(0.01)

        res = await apply_filter(userID=msg["userID"], filterName=msg["filterName"], imageID=imageID)

        return res
    except Exception as e:
        app.state.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/filter")
async def test_filter(filterName: str = Query(...), imageID: str = Query(...)):   
    # Temporaly hardcode userID = "user1"
    userID = "user1" 
    res = await apply_filter(userID=userID, filterName=filterName, imageID=imageID)
    return res
############################
# Main Service
############################
async def consume_messages():
    while True:
        msg = await app.state.broker.get() # Return a dict
        if msg:
            await apply_filter(msg["userID"], msg["filterName"])
        await asyncio.sleep(0.01)

async def apply_filter(userID: str, filterName: str, imageID: str):
    if filterName not in FILTER_MAP:
        app.state.logger.error(f"Unknown filter: {filterName}")
        raise ValueError(f"Unknown filter: {filterName}")

    # Download image from MinIO
    try:
        image_bytes = app.state.imgBucket.download_image_from_s3(imageID)
        image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        app.state.logger.error(f"Image not found in MinIO: {imageID}")
        raise

    # Apply the filter
    filtered = FILTER_MAP[filterName](image_np)

    # Encode image to JPEG
    success, buffer = cv2.imencode(".jpg", filtered)
    if not success:
        app.state.logger.error(f"Failed to encode image: {imageID}")
        raise

    return Response(content=buffer.tobytes(), media_type="image/jpeg")

