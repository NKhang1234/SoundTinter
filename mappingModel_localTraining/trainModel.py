import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import logging
import sys

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
LOGGING_LEVEL = "debug"

logLevel = level_map.get(LOGGING_LEVEL.lower(), logging.INFO)

logging.basicConfig(
    level=logLevel,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

log = logging.getLogger(__name__)

def trainDecisionTree(dataset_path: str):
    # Load dataset from CSV
    try:
        df = pd.read_csv(dataset_path)
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

    model_path = 'models/decisionTree.pkl'

    joblib.dump({
        "model": clf,
        "key_enc": key_enc,
        "scale_enc": scale_enc,
        "filter_enc": filter_enc,
    }, model_path)

    log.info(f"✅ Model saved to {model_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: trainModel.py [model name] [dataset path (.csv)]")
        print("""Model list (Model - Model name):""")
        print("""- Decision Tree: DecisionTree""")
        sys.exit(1)
    
    if sys.argv[1] == "DecisionTree":
        trainDecisionTree(dataset_path=sys.argv[2])
    else:
        print(f"❌ Unknown model: {model_name}")
        print("Available models: DecisionTree")
        sys.exit(1)
    
