from fastapi import FastAPI, UploadFile, File, HTTPException
from essentiaWrapper import EssentiaExtractor
import json
from exceptions import FileReadError
from s3_utils import SongBucket

app = FastAPI()
extractor = EssentiaExtractor()
bucket = SongBucket()


@app.post("/analyze-song")
async def analyze_song(file: UploadFile = File(...)):
    try:
        try:
            audio_data = await file.read()
        except Exception as e:
            raise FileReadError("Failed to read audio") from e

        bucket.upload_song_to_s3(filename=file.filename, data=audio_data, content_type=file.content_type)
        features = extractor.extract_from_bytes(audio_data)
        return features

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Song Analyst Service is running"}
