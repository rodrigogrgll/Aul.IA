import google.generativeai as genai
import streamlit as st # Usamos streamlit solo para leer el secreto
import os

# --- Configura la API Key desde el archivo secrets.toml ---
# Esto asume que estás ejecutando este script desde la carpeta Aul_IA_TFM
# y que tu secrets.toml está en .streamlit/secrets.toml
try:
    # Esto es un truco para que python encuentre la carpeta .streamlit
    os.environ["STREAMLIT_PATH"] = ".streamlit" 

    # Leemos el secreto
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)

    print("¡API Key configurada con éxito!")
    print("--- Modelos a los que SÍ tienes acceso ---")

    # --- Aquí está la magia: Pedimos la lista de modelos ---
    for model in genai.list_models():
        # Buscamos modelos que SÍ se puedan usar para generar contenido
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")

    print("-------------------------------------------------")

except Exception as e:
    print(f"ERROR: No se pudo configurar la API Key o listar modelos.")
    print(f"Asegúrate de que .streamlit/secrets.toml existe y es correcto.")
    print(f"Error detallado: {e}")