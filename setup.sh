#!/bin/bash

# Create .streamlit config directory
mkdir -p ~/.streamlit/

# Write the Streamlit server config
cat <<EOF > ~/.streamlit/config.toml
[server]
headless = true
port = \$PORT
enableCORS = false
EOF

# Install Python packages
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
