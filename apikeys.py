import streamlit as st

# Reads keys from .streamlit/secrets.toml (local) or
# Streamlit Cloud > App Settings > Secrets (deployed)
openrouter_api = st.secrets["openrouter_api"]
news_API       = st.secrets["news_API"]
