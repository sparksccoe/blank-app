FROM python:3.11-slim

# Install libsndfile (needed by soundfile) in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 libportaudio2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements FIRST — this layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code SECOND — only this layer rebuilds on code changes
COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "DA_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]