from fastapi import FastAPI, Query, Response, HTTPException
import numpy as np
import cv2

from s3_utils import download_image_from_s3
from filters import FILTER_MAP

app = FastAPI()

# Temporary hardcoded song-to-filter mapping
SONG_FILTER_MAP = {
    "song1": "sepia",
    "song2": "grayscale",
    "song3": "blur",
    "song4": "gotham",
    "song5": "warm",
    "song6": "cold"
}

@app.get("/apply_filter/")
def apply_filter(song_id: str = Query(...), image_id: str = Query(...)):
    # Get filter type from hardcoded map - Simluate call API from MappingService
    filter_type = SONG_FILTER_MAP.get(song_id, "sepia")  # default to sepia

    if filter_type not in FILTER_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown filter: {filter_type}")

    # Download image from MinIO
    try:
        image_bytes = download_image_from_s3(image_id)
        image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found in MinIO: {str(e)}")

    # Apply the filter
    filtered = FILTER_MAP[filter_type](image_np)

    # Encode image to JPEG
    success, buffer = cv2.imencode(".jpg", filtered)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image")

    return Response(content=buffer.tobytes(), media_type="image/jpeg")
