FROM ghcr.io/mtg/essentia:bullseye-v2.1_beta5

# Work inside /app
WORKDIR /app

# Install pip for Python 3.9
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better Docker cache use)
COPY requirements.txt /app

# Install Python dependencies into system Python 3.9
RUN /usr/bin/python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . /app

# Run FastAPI with system Python 3.9
CMD ["/usr/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
