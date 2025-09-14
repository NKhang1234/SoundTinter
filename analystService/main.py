from fastapi import FastAPI, UploadFile, File, HTTPException
from essentiaWrapper import EssentiaExtractor
import json
from exceptions import FileReadError
from s3_utils import SongBucket
from dynamoDB_utils import FeatureDynamo
from config import DYNAMODB_PARTITION_KEY, DYNAMODB_SORT_KEY

app = FastAPI()
extractor = EssentiaExtractor()
songBucket = SongBucket()
featDyna = FeatureDynamo()



@app.post("/test/analyze-song")
async def analyze_song(file: UploadFile = File(...)):
    try:
        try:
            audio_data = await file.read()
        except Exception as e:
            raise FileReadError("Failed to read audio") from e

        if songBucket.check_if_exist(fileName=file.filename):
            raise FileExistsError(f"{file.filename} already exists in bucket")

        features = extractor.extract_from_bytes(audio_data)
        features[DYNAMODB_PARTITION_KEY] = "user1" # Temparily hard code userID of user as partition key in DynamoDB
        features[DYNAMODB_SORT_KEY] = file.filename

        featDyna.add_item(features)
        songBucket.upload_song_to_s3(fileName=file.filename, data=audio_data, contentType=file.content_type)
        return features

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Song Analyst Service is running"}
