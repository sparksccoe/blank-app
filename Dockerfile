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

# Streamlit uses this port
ENV PORT=8501

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=$PORT", "--server.address=0.0.0.0"]
