# "import" significa: "Carga la caja de herramientas de Streamlit y llámala 'st'"
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config() pone la página en modo "ancho" (wide)
st.set_page_config(layout="wide") 

# 1. TÍTULO (Acción 2, Cambio 1)
st.title("Aul.IA: Creación de Situaciones de Aprendizaje")

# --- CREACIÓN DE PANELES (Acción 2, Cambio 5) ---
# Creamos dos columnas. La de la izquierda (1) será 1/3 del ancho
# y la de la derecha (2) será 2/3.
col1, col2 = st.columns([1, 2])

# --- PANEL DERECHO (col2): LOS CONTROLES (Acción 2, Cambio 2) ---
with col2:
    st.subheader("Paso 1: Define tus 5 variables")

    # 2.1: CURSO (Con Primaria)
    curso = st.selectbox(
        "Elige el curso:", 
        ("3º Primaria", "4º Primaria", "5º Primaria", "6º Primaria", 
         "1º ESO", "2º ESO", "3º ESO", "4º ESO", "1º Bachillerato", "2º Bachillerato")
    )

    # 2.2: TEMA (Nuevo)
    tema = st.text_input(
        "Contenido concreto o pretexto (ej: 'Los Volcanes', 'El Antiguo Egipto'):"
    )

    # 2.3: CE (Competencia Específica)
    competencia = st.text_area(
        "Pega aquí la Competencia Específica (CE) principal:",
        height=100
    )

    # 2.4: CEv (Criterio de Evaluación) (Nuevo)
    criterio_eval = st.text_area(
        "Pega aquí el Criterio de Evaluación (CEv) asociado:",
        height=100
    )

    # 2.5: SB (Saberes Básicos) (Renombrado, no opcional)
    saberes = st.text_area(
        "Selecciona los Saberes Básicos (SB) curriculares:", 
        # (Aquí pondrías los reales)
        height=100)

# --- PANEL IZQUIERDO (col1): LOS RESULTADOS (Acción 2, Cambio 5) ---
with col1:
    st.subheader("Paso 2: Plan de Foco Estratégico")

    # Este 'st.empty()' es un truco. Es una "caja vacía" que
    # rellenaremos más tarde (en la Acción 4) con el plan de foco.
    output_plan_foco = st.empty()

    output_plan_foco.info("El Plan de Foco generado por la IA aparecerá aquí...")

# --- ZONA DE BOTONES (Acción 2, Cambios 4, 6, 7) ---
st.divider() # Una línea divisoria antes de los botones
st.subheader("Paso 3: Generación")

# Creamos dos columnas para los botones en la parte inferior
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Botón 1: "Seleccionar variables para la SA"
    if st.button("Generar Plan de Foco Estratégico", use_container_width=True):
        # La lógica de este botón la definiremos en la Acción 4
        pass # 'pass' significa "no hagas nada todavía"

with col_btn2:
    # Botón 2: "Crear Situación de Aprendizaje"
    if st.button("Crear Situación de Aprendizaje", use_container_width=True, type="primary"):
        # La lógica de este botón la definiremos en la Acción 5
        pass # 'pass' significa "no hagas nada todavía"