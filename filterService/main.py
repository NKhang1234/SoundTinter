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
from config import S3_ORIGINAL_BUCKET, S3_RESULT_BUCKET

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
    app.state.imgBucket = ImageBucket(S3_ORIGINAL_BUCKET)
    app.state.resultImgBucket = ImageBucket(S3_RESULT_BUCKET)
    if APP_ENV == "prod":
        app.state.logger.info("FilterService is in PRODUCTION mode")
    elif APP_ENV == "dev":
        # Initiate RabbitMQ
        app.state.broker: MessageBroker = RabbitMQ("FilterService")
        await app.state.broker.connect() # Asynchronous connect app to RabbitMQ server
        asyncio.create_task(consume_messages()) # Run a concurrent background loop to fetch message from RabbitMQ 

        app.state.logger.info("FilterService is in DEVELOPMENT mode")
@app.on_event("shutdown")
async def shutdown_event():
    if APP_ENV == "dev":
        await app.state.broker.close()

############################
# HTTP API
############################  
@app.post("/request_filter")
async def request_filter(
    songName: str = Query(...), 
    imageName: str = Query(...),
    x_user_id: str = Header(...),
):
    try:
        image_key = f"users/{x_user_id}/images/{imageName}"
        await app.state.broker.send(userID=x_user_id, songName=songName, imageID=image_key)
    except Exception as e:
        app.state.logger.error(f"Failed to send mapping request to MappingService| song name: {songName}, user: {x_user_id}")
        raise HTTPException(status_code=500, detail=str(e))
 
    return {"message": "Filter request sent successfully"}

@app.get("/get_result")
async def get_result(
    songName: str = Query(...), 
    imageName: str = Query(...),
    x_user_id: str = Header(...),
):   
    res_key = f"users/{x_user_id}/images/{imageName}/songs/{songName}"
    try:
        res_image = app.state.resultImgBucket.download_image_from_s3(image_id=res_key)
    except Exception as e:
        app.state.logger.error(f"Filtered image not found in S3 | userID: {x_user_id}, songName: {songName}, imageName: {imageName}")
        raise HTTPException(status_code=404, detail="Filtered image not found")

    return Response(content=res_image, media_type="image/jpeg")


############################
# HTTP API for test
############################
@app.post("/test/filter")
async def test_filter(
    filterName: str = Query(...), 
    imageName: str = Query(...),
    x_user_id: str = Header(...),
):   
    image_key = f"users/{x_user_id}/images/{imageName}"
    res = await apply_filter(filterName=filterName, imageID=image_key)
    return res
############################
# Main Service
############################
async def consume_messages():
    while True:
        msg = await app.state.broker.get() # Return a dict
        if msg:
            userID = msg["userID"]
            filterName = msg["filterName"]
            imageID = msg["imageID"]
            songName = msg["songName"]
            app.state.logger.debug(f"Received message from RabbitMQ | userID: {userID}, filter: {filterName}, imageID: {imageID}, songName: {songName}")
            
            res_image = await apply_filter(filterName, imageID)
            res_key = f"{imageID}/songs/{songName}"
            app.state.resultImgBucket.upload_image_to_s3(image_id=res_key, image_bytes=res_image.body)
            app.state.logger.info(f"Filtered image uploaded to S3 | userID: {userID}, filter: {filterName}, imageID: {imageID}, songName: {songName}")
        await asyncio.sleep(0.01)

async def apply_filter(filterName: str, imageID: str):
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

    return buffer.tobytes()

