# 🎵 Song-to-Filter Mapping Model Training

This module trains a **Decision Tree model** to map **audio features** (BPM, danceability, loudness, key, scale) to a corresponding **image filter**.  
The resulting model (`model.pkl`) will be used by the **Mapping Service** in your main application to predict which image filter matches a given song.

---

## 🧩 Project Structure
training/
│
├── trainModel.py # Training script
├── dataset.csv # Training dataset (≈120 rows)
├── requirements.txt # Dependencies
└── model.pkl # Trained model (generated)


---
## ⚙️ Running
### 1. Create and Activate Virtual Environment (Linux)

Create a Python virtual environment for local training.

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Train Model
python3 trainModel.py [model name] [dataset(.csv)] [model path]
python3 trainModel.py DecisionTree dataset.csv model.pkl
