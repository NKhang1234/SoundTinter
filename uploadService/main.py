from fastapi import FastAPI, UploadFile, File, HTTPException
import json
from s3_utils import ImageBucket()

app = FastAPI()

imgBucket = ImageBucket()


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        try:
            image_data = file.read()
        except Exception as e:
            raise FileReadError("Failed to read image") from e
        
        imgBucket.upload_image_to_s3(fileName=file.filename, data=image_data, contentType=file.content_type)

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-song")
async def upload_song(file: UploadFile = File(...)):
    try: 
        try:
            song_data = file.read()
        except Exception as e:
            raise FileReadError("Failed to read image") from e

            # ..... Push to RabbitMQ
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))