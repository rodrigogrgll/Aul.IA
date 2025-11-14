# "import" significa: "Carga la caja de herramientas de Streamlit y llámala 'st'"
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config() pone la página en modo "ancho" (wide)
st.set_page_config(layout="wide") 

# --- AÑADIR EL FONDO (MÉTODO CSS ROBUSTO) ---

# Define el color de fondo base para tu aplicación (de tu paleta)
background_color = "#F5F7FA" # Azul pálido
svg_line_color = "#DEE2E6" # Color de trazo

st.markdown(
    f"""
    <style>
    /* Esta es la forma más robusta de poner un fondo en Streamlit.
      Apunta directamente al contenedor principal .stApp.
    */
    .stApp {{
        background-color: {background_color};
        
        /* Creamos un patrón de "papel milimetrado" usando gradientes CSS.
           Es ligero, no da errores y encaja con el tema de "plano".
        */
        background-image: 
            linear-gradient(to right, {svg_line_color} 0.5px, transparent 0.5px),
            linear-gradient(to bottom, {svg_line_color} 0.5px, transparent 0.5px);
        
        /* Definimos el tamaño de la cuadrícula */
        background-size: 20px 20px; 
        
        /* 'scroll' es el valor por defecto, lo que significa que el fondo
           se moverá junto con el contenido cuando el usuario haga scroll.
           Esto cumple tu última petición.
        */
        background-attachment: scroll; 
    }}
    </style>
    """,
    unsafe_allow_html=True
)


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
    # Botón 1: "Generar Plan de Foco Estratégico"
    if st.button("Generar Plan de Foco Estratégico", use_container_width=True):
        # La lógica de este botón la definiremos en la Acción 4
        pass # 'pass' significa "no hagas nada todavía"

with col_btn2:
    # Botón 2: "Crear Situación de Aprendizaje"
    if st.button("Crear Situación de Aprendizaje", use_container_width=True, type="primary"):
        # La lógica de este botón la definiremos en la Acción 5
        pass # 'pass' significa "no hagas nada todavía"

# --- CUADRO DE TEXTO PARA LA SITUACIÓN DE APRENDIZAJE (NUEVO Y CORREGIDO) ---
st.markdown("---") # Pequeño separador visual
st.subheader("Paso 4: Situación de Aprendizaje Generada")
output_sa = st.text_area(
    "La Situación de Aprendizaje completa generada por la IA aparecerá aquí:",
    value="Pulsa 'Crear Situación de Aprendizaje' para que la IA elabore el texto completo aquí.",
    height=400, # Altura generosa para el contenido
    help="Este campo no es editable y mostrará el resultado final.",
    disabled=True # Hace que el campo no sea editable
)

# (La línea 'output_sa.text(...)' que estaba aquí se ha borrado porque ahora está en 'value')