FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Optional: Symbolic port exposure
EXPOSE 8501

# Final CMD: Streamlit binds to $PORT from Railway
CMD streamlit run DA_app.py --server.port=$PORT --server.address=0.0.0.0
