#!/bin/bash

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

pip install -r requirements.txt

# DO NOT put $PORT in the config file — only pass it here
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT
