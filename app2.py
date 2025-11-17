# "import" significa: "Carga la caja de herramientas de Streamlit y llámala 'st'"
import streamlit as st
import google.generativeai as genai # La librería que ya instalaste

# Cargar la API Key desde los secretos
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except FileNotFoundError:
    st.error("No se encontró el archivo secrets.toml. Asegúrate de crearlo en la carpeta .streamlit.")
except KeyError:
    st.error("No se encontró la GOOGLE_API_KEY en secrets.toml. Asegúrate de añadirla.")

# --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config() pone la página en modo "ancho" (wide)
st.set_page_config(layout="wide") 

# --- AÑADIR EL FONDO SVG (NUEVO MÉTODO CORREGIDO) ---

# Define el color de fondo base para tu aplicación (de tu paleta)
background_color = "#F5F7FA" # Azul pálido
svg_stroke_color = "#DEE2E6" # Color de trazo apenas visible

st.markdown(
    f"""
    <style>
    /* 1. Estilo para el fondo de la página (ahora en el body) */
    body {{
        background-color: {background_color};
        position: relative; /* Ancla para el SVG */
        min-height: 100vh; /* Asegura que el body ocupe al menos la pantalla */
    }}

    /* 2. Hacemos transparente el contenedor principal de Streamlit */
    .stApp {{
        background-color: transparent;
    }}

    /* 2b. !!LA CORRECCIÓN CLAVE!! */
    /* Hacemos transparente el "lienzo" principal donde Streamlit pone el contenido */
    /* Este es el bloque que tiene el fondo blanco/gris por defecto */
    [data-testid="stAppViewContainer"] > .main {{
        background-color: transparent;
    }}


    /* 3. Contenedor del SVG de fondo (ahora se mueve con el scroll) */
    .background-svg {{
        position: absolute; 
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;       /* 100% del body (que tiene min-height) */
        z-index: -1;
    }}

    /* 4. Estilos para las formas dentro del SVG */
    .stroke-style {{
        stroke: {svg_stroke_color};
        stroke-width: 1px;
        fill: none;
    }}
    .node-circle {{
        r: 3;
        fill: {svg_stroke_color};
        stroke: none;
    }}
    .node-rect {{
        width: 6;
        height: 6;
        rx: 1;
        fill: {svg_stroke_color};
        stroke: none;
    }}
    .node-poly {{
        points: '5,0 9.33,2.5 9.33,7.5 5,10 0.67,7.5 0.67,2.5';
        fill: {svg_stroke_color};
        stroke: none;
    }}
    </style>

    <!-- 5. El SVG de fondo como un elemento HTML separado -->
    <svg class='background-svg' viewBox='0 0 1000 1000' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>
        <!-- Red de Conexiones --><path d='M100 100 L250 150 L300 300 L150 400 L50 250 Z' class='stroke-style'/>
        <path d='M400 50 L500 200 L650 100 L700 300' class='stroke-style'/>
        <path d='M100 500 Q200 600, 300 500 T400 600' class='stroke-style'/>
        <path d='M500 450 C600 400, 700 550, 800 500' class='stroke-style'/>
        <path d='M850 150 L950 200 L900 350 L750 300 Z' class='stroke-style'/>
        <path d='M200 800 L350 700 L400 900 L250 950 Z' class='stroke-style'/>
        <path d='M600 700 Q700 600, 800 700 T900 600' class='stroke-style'/>
        <!-- Nodos Geométricos --><circle cx='100' cy='100' class='node-circle'/>
        <rect x='247' y='147' class='node-rect'/>
        <polygon transform='translate(295 295)' class='node-poly'/>
        <circle cx='150' cy='400' class='node-circle'/>
        <rect x='49' y='247' class='node-rect'/>
        <circle cx='400' cy='50' class='node-circle'/>
        <rect x='497' y='197' class='node-rect'/>
        <polygon transform='translate(645 95)' class='node-poly'/>
        <circle cx='700' cy='300' class='node-circle'/>
        <circle cx='100' cy='500' class='node-circle'/>
        <rect x='397' y='597' class='node-rect'/>
        <circle cx='500' cy='450' class='node-circle'/>
        <rect x='797' y='497' class='node-rect'/>
        <circle cx='850' cy='150' class='node-circle'/>
        <rect x='947' y='197' class='node-rect'/>
        <polygon transform='translate(895 345)' class='node-poly'/>
        <circle cx='750' cy='300' class='node-circle'/>
        <circle cx='200' cy='800' class='node-circle'/>
        <rect x='347' y='697' class='node-rect'/>
        <polygon transform='translate(395 895)' class='node-poly'/>
        <circle cx='250' cy='950' class='node-circle'/>
        <circle cx='600' cy='700' class='node-circle'/>
        <rect x='897' y='597' class='node-rect'/>
        <!-- Iconos Conceptuales --><path d='M60 70 L60 80 A10 10 0 0 0 70 90 A10 10 0 0 0 80 80 L80 70 A10 10 0 0 0 70 60 A10 10 0 0 0 60 70 Z M68 90 L72 90 M68 93 L72 93' transform='scale(0.8) translate(700 800)' class='stroke-style'/>
        <path d='M60 70 L60 80 A10 10 0 0 0 70 90 A10 10 0 0 0 80 80 L80 70 A10 10 0 0 0 70 60 A10 10 0 0 0 60 70 Z M68 90 L72 90 M68 93 L72 93' transform='scale(0.8) translate(100 300)' class='stroke-style'/>
        <path d='M50 50 A20 20 0 1 1 50 50.001 M45 50 L55 50 M50 45 L50 55 M58 43 L62 41 M41 58 L39 62 M43 62 L41 58 M58 57 L62 59 M38 43 L34 39 M57 38 L59 34' transform='scale(1.2) translate(150 650)' class='stroke-style'/>
        <path d='M50 50 A20 20 0 1 1 50 50.001 M45 50 L55 50 M50 45 L50 55 M58 43 L62 41 M41 58 L39 62 M43 62 L41 58 M58 57 L62 59 M38 43 L34 39 M57 38 L59 34' transform='scale(1.2) translate(700 50)' class='stroke-style'/>
        <path d='M50 0 L50 20 L70 20 L70 40 L50 40 L50 60 L30 60 L30 40 L10 40 L10 20 L30 20 L30 0 Z' transform='scale(0.8) translate(400 200)' class='stroke-style'/>
        <path d='M50 0 L50 20 L70 20 L70 40 L50 40 L50 60 L30 60 L30 40 L10 40 L10 20 L30 20 L30 0 Z' transform='scale(0.8) translate(800 700)' class='stroke-style'/>
        <circle cx='40' cy='40' r='30' class='stroke-style' transform='translate(500 50) scale(0.8)'/>
        <circle cx='60' cy='40' r='30' class='stroke-style' transform='translate(500 50) scale(0.8)'/>
        <circle cx='40' cy='40' r='30' class='stroke-style' transform='translate(100 850) scale(0.8)'/>
        <circle cx='60' cy='40' r='30' class='stroke-style' transform='translate(100 850) scale(0.8)'/>
        <path d='M20 50 A15 15 0 1 0 50 50 A15 15 0 1 0 80 50 M10 70 Q30 55, 50 70 Q70 55, 90 70 Z' transform='scale(0.7) translate(300 400)' class='stroke-style'/>
        <path d='M20 50 A15 15 0 1 0 50 50 A15 15 0 1 0 80 50 M10 70 Q30 55, 50 70 Q70 55, 90 70 Z' transform='scale(0.7) translate(850 450)' class='stroke-style'/>
    </svg>
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