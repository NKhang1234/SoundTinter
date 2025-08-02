from fastapi import FastAPI, UploadFile, File, HTTPException
from acrCloud_client import ACRCloudClient as acrCloud
import json

app = FastAPI()


@app.post("/analyze-song")
async def analyze_song(file: UploadFile = File(...)):
    try:
        acr = acrCloud()
        print(f"Received file: {file.filename}")

        # Read uploaded file into bytes
        audio_data = await file.read()

        # Identify the song using ACRCloud
        song_info = acr.identify_song(audio_data)
        print("ACRCloud result:", json.dumps(song_info, indent=2))

        return song_info

        # Try to extract Spotify track ID
        # try:
        #     track_id = song_info["metadata"]["music"][0]["external_metadata"]["spotify"]["track"]["id"]
        # except (KeyError, IndexError):
        #     raise HTTPException(status_code=404, detail="Spotify track ID not found in ACRCloud response")

        # # Fetch song features from Spotify API
        # access_token = spotify_client.get_access_token()
        # song_features = spotify_client.get_song_features(track_id, access_token)
        # print("Spotify features:", song_features)

        # return {
        #     "song_info": song_info,
        #     "song_features": song_features
        # }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Song Analyst Service is running"}
