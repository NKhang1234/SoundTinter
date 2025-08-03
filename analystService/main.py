from fastapi import FastAPI, UploadFile, File, HTTPException
from acrCloud_client import ACRCloudClient
from spotify_client import SpotifyClient
import json

app = FastAPI()
acr = ACRCloudClient()
spotify = SpotifyClient()


@app.post("/analyze-song")
async def analyze_song(file: UploadFile = File(...)):
    try:
        audio_data = await file.read()

        # Indentify song by acrCloud
        song_info = acr.identify_song(audio_data)
        print("hello")

        try:
            track_id = song_info["metadata"]["music"][0]["external_metadata"]["spotify"]["track"]["id"]
        except (KeyError, IndexError):
            raise HTTPException(status_code=404, detail="Spotify track ID not found in ACRCloud response")

        # Fetch song features from Spotify API
        song_features = await spotify.get_song_features(track_id)
        print(track_id)
        # print(f'song features: '{song_features})

        return {
            "song_info": song_info,
            "song_features": song_features
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Song Analyst Service is running"}
