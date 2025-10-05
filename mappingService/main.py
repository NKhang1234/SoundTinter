from fastapi import FastAPI
from pydantic import BaseModel
from mappingEngine import MappingEngine
from config import MODEL_PATH

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
    app.state.featDyna = FeatureDynamo()
    app.state.mapEngine = MappingEngine(MODEL_PATH)

    if APP_ENV == "prod":
        app.state.logger.info("MappingService is in PRODUCTION mode")
    elif APP_ENV == "dev":
        # Initiate RabbitMQ
        app.state.broker: MessageBroker = RabbitMQ("MappingService")
        await app.state.broker.connect() # Asynchronous connect app to RabbitMQ server
        asyncio.create_task(consume_messages()) # Run a concurrent background loop to fetch message from RabbitMQ 

        app.state.logger.info("MappingService is in DEVELOPMENT mode")

@app.on_event("shutdown")
async def shutdown_event():
    if APP_ENV == "dev":
        await app.state.broker.close()

############################
# HTTP API for test
############################
@app.post("/test/mapping")
async def mapping(userID: str, songName: str):
    try:
        filterName = await map_filter(userID=userID, songName=songName)
        return {
            "userID": userID,
            "songName": songName,
            "filterName": filterName
        }
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
            app.state.logger.info(f"MappingService")
            await analyze_song(msg["userID"], msg["songName"])
        await asyncio.sleep(0.01)

async def map_filter(userID: str, songName: str) -> dict:
    try:
        features = app.state.featDyna.get_item(partition_key=userID, sort_key=songName)
    except Exception as e:
        app.state.logger.error(f"Failed to get song features from DynamoDB: {userID} - {songName}")

    try:
        filter_name = app.state.mapEngine.predict_filter({
            "rhythm.bpm": features.rhythm_bpm,
            "rhythm.danceability": features.rhythm_danceability,
            "lowlevel.average_loudness": features.lowlevel_average_loudness,
            "tonal.chords_key": features.tonal_chords_key,
            "tonal.chords_scale": features.tonal_chords_scale,
        })
    except Exception as e:
        app.state.logger.error(f"Failed map song to filter in mapping engine: {userID} - {songName}")
        raise
    
    await app.state.broker.send(self, userID=userID, filterName=filter_name, status="Successfully")

    # Testing usage
    return filter_name

@app.get("/")
def root():
    return {"message": "Mapping Service is running"}

