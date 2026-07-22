FROM python:3.11-slim

WORKDIR /app

# Copy requirements FIRST — this layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code SECOND — only this layer rebuilds on code changes
COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "DA_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]