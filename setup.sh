#!/bin/bash

# Install system-level PortAudio
apt-get update && apt-get install -y portaudio19-dev

# Create .streamlit config
mkdir -p ~/.streamlit/
cat <<EOF > ~/.streamlit/config.toml
[theme]
primaryColor = '#DB661D'
backgroundColor = '#FBFBFA'
secondaryBackgroundColor = '#AD98B0'
textColor = '#2D2B3E'
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = false
EOF

# Install Python dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
