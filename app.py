# "import" significa: "Carga la caja de herramientas de Streamlit y llámala 'st'"
import streamlit as st

# st.title(...) es una orden: "Streamlit, pon este título en el NAVEGADOR WEB"
st.title("💎 Aul.IA: Salón de Diseño")
st.subheader("Paso 1: Define tu encargo")

st.info("Introduce las 5 variables para que nuestro 'Diseñador Jefe' (IA) cree tu plan de foco.")

# --- RECOGIDA DE VARIABLES ---

# st.selectbox(...) crea un menú desplegable en el NAVEGADOR.
# Lo que el usuario elija, se guarda en la variable 'curso'.
curso = st.selectbox(
    "Elige el curso:", 
    ("1º ESO", "2º ESO", "3º ESO", "4º ESO", "1º Bachillerato", "2º Bachillerato")
)

# st.text_area(...) crea una caja de texto grande.
# Lo que el usuario escriba se guarda en la variable 'competencia'.
competencia = st.text_area(
    "Pega aquí la Competencia Específica (o el texto del 'plano'):",
    height=150 # Le damos un poco de altura
)

# st.slider(...) crea una barra deslizante.
# El número que elija se guarda en la variable 'sesiones'.
sesiones = st.slider(
    "Nº de sesiones:", 
    min_value=1,  # Valor mínimo
    max_value=10, # Valor máximo
    value=3       # Valor por defecto
)

# st.text_input(...) crea una caja de texto simple.
materia = st.text_input("Materia (ej: 'Biología y Geología'):")

# st.multiselect(...) permite elegir varias opciones.
# Las opciones elegidas se guardan como una LISTA en la variable 'saberes'.
saberes = st.multiselect(
    "Saberes a priorizar (opcional):", 
    ["Saber A", "Saber B", "Saber C", "Saber D"]
)