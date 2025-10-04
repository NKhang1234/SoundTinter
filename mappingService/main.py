from fastapi import FastAPI
from pydantic import BaseModel
from mappingEngine import MappingEngine

app = FastAPI()
engine = None  # global singleton

class SongFeatures(BaseModel):
    rhythm_bpm: float
    rhythm_danceability: float
    lowlevel_average_loudness: float
    tonal_chords_key: str
    tonal_chords_scale: str

@app.on_event("startup")
def load_model():
    global engine
    engine = MappingEngine("model.pkl")
    print("✅ Decision Tree model loaded successfully")

@app.post("/map")
async def map_filter(features: SongFeatures):
    filter_name = engine.predict_filter({
        "rhythm.bpm": features.rhythm_bpm,
        "rhythm.danceability": features.rhythm_danceability,
        "lowlevel.average_loudness": features.lowlevel_average_loudness,
        "tonal.chords_key": features.tonal_chords_key,
        "tonal.chords_scale": features.tonal_chords_scale,
    })
    return {"filter": filter_name}
