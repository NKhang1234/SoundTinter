import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import logging
import sys

def trainDecisionTree(model_path: str = "model.pkl"):
    data = [
        {"bpm": 80,  "danceability": 0.3, "loudness": -15, "key": "A", "scale": "minor", "filter": "willow"},
        {"bpm": 100, "danceability": 0.6, "loudness": -10, "key": "C", "scale": "major", "filter": "gingham"},
        {"bpm": 120, "danceability": 0.8, "loudness": -5,  "key": "G", "scale": "major", "filter": "clarendon"},
        {"bpm": 140, "danceability": 0.9, "loudness": -3,  "key": "D", "scale": "major", "filter": "lofi"},
        {"bpm": 90,  "danceability": 0.4, "loudness": -12, "key": "E", "scale": "minor", "filter": "aden"},
    ]
    df = pd.DataFrame(data)

    # Load dataset from CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        log.error(f"❌ Failed to load dataset: {e}")
        sys.exit(1)

    # Expected columns: bpm, danceability, loudness, key, scale, filter
    required_columns = {"bpm", "danceability", "loudness", "key", "scale", "filter"}
    if not required_columns.issubset(df.columns):
        log.error(f"❌ Dataset must contain columns: {required_columns}")
        sys.exit(1)

    key_enc = LabelEncoder()
    scale_enc = LabelEncoder()
    filter_enc = LabelEncoder()

    df["key_enc"] = key_enc.fit_transform(df["key"])
    df["scale_enc"] = scale_enc.fit_transform(df["scale"])
    df["filter_enc"] = filter_enc.fit_transform(df["filter"])

    X = df[["bpm", "danceability", "loudness", "key_enc", "scale_enc"]]
    y = df["filter_enc"]

    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    clf.fit(X, y)

    joblib.dump({
        "model": clf,
        "key_enc": key_enc,
        "scale_enc": scale_enc,
        "filter_enc": filter_enc,
    }, model_path)

    log.info(f"✅ Model saved to {model_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: trainModel.py [model name] [model path]")
        print("""Model list (Model - Model name):""")
        print("""- Decision Tree: DecisionTree""")
        sys.exit(1)
    
    if sys.argv[1] == "DecisionTree":
        trainDecisionTree(sys.argv[2])
    else:
        print(f"❌ Unknown model: {model_name}")
        print("Available models: DecisionTree")
        sys.exit(1)
    
