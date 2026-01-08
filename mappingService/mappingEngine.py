import joblib
import numpy as np

class MappingEngine:
    def __init__(self, model_path: str = "model.pkl"):
        model_bundle = joblib.load(model_path)
        self.model = model_bundle["model"]
        self.key_enc = model_bundle["key_enc"]
        self.scale_enc = model_bundle["scale_enc"]
        self.filter_enc = model_bundle["filter_enc"]

    def predict_filter(self, features: dict) -> str:
        bpm = float(features.get("rhythm.bpm", 120))
        dance = float(features.get("rhythm.danceability", 0.5))
        loud = float(features.get("lowlevel.average_loudness", -10))
        key = features.get("tonal.chords_key", "C")
        scale = features.get("tonal.chords_scale", "major")

        key_val = (
            self.key_enc.transform([key])[0]
            if key in self.key_enc.classes_
            else 0
        )
        scale_val = (
            self.scale_enc.transform([scale])[0]
            if scale in self.scale_enc.classes_
            else 0
        )

        X_pred = np.array([[bpm, dance, loud, key_val, scale_val]])
        y_pred = self.model.predict(X_pred)[0]
        return self.filter_enc.inverse_transform([y_pred])[0]
