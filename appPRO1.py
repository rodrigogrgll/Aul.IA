import streamlit as st
import google.generativeai as genai
import time
import markdown
from xhtml2pdf import pisa
import io
import streamlit.components.v1 as components # Para el hack del scroll
import pandas as pd # IMPORTANTE: Añadido para manejar datos

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Aul.IA - Diseño de Situaciones de Aprendizaje",
    page_icon="✨",
    layout="wide"
)

# --- JAVASCRIPT PARA SCROLL CINEMÁTICO ---
def scroll_to_top():
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = 0;
    </script>
    '''
    components.html(js, height=0)

# --- GESTIÓN DE ESTADO (WIZARD) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'input_curso' not in st.session_state: st.session_state.input_curso = "Selecciona un curso..."
if 'input_tema' not in st.session_state: st.session_state.input_tema = ""
if 'input_ce' not in st.session_state: st.session_state.input_ce = ""
if 'input_cev' not in st.session_state: st.session_state.input_cev = ""
# Nuevas variables incorporadas
if 'input_bloque' not in st.session_state: st.session_state.input_bloque = ""
if 'input_subapartado' not in st.session_state: st.session_state.input_subapartado = ""
if 'input_sb' not in st.session_state: st.session_state.input_sb = ""

# Memoria de la IA
if 'plan_de_foco' not in st.session_state: st.session_state.plan_de_foco = None
if 'plan_json' not in st.session_state: st.session_state.plan_json = None    
if 'sa_generada' not in st.session_state: st.session_state.sa_generada = None
if 'editor_sa' not in st.session_state: st.session_state.editor_sa = "Pulsa 'Crear Situación de Aprendizaje' para generar el contenido."

# --- API KEY ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except FileNotFoundError:
    st.error("No se encontró el archivo secrets.toml.")
except KeyError:
    st.error("No se encontró la GOOGLE_API_KEY en secrets.toml.")

# --- MODELO ---
model = genai.GenerativeModel('models/gemini-2.5-pro')

# ==============================================================================
# LOGICA DE DATOS (IMPORTADA DEL CÓDIGO 1)
# ==============================================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRp8yJQGCVyGEbrNn0zgEzy5-iLxhnS4fpA7oV6yA5bPA95wW6V0waRm78c6rea_A/pub?gid=650080582&single=true&output=csv" 
SHEET_SABERES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMvw6czNW_kcLWRp8WsxLfqc9FsYwb1Zi5rQmFMh7sQPRNUrH7yk0eNHXPxFQk8w/pub?gid=1639548304&single=true&output=csv" 

@st.cache_data 
def cargar_datos_csv(url):
    try:
        if "PON_AQUI" in url: return None 
        # 1. Intentamos leer con coma
        df = pd.read_csv(url, sep=",")
        # 2. Si solo hay 1 columna, probamos con punto y coma
        if len(df.columns) <= 1:
            df = pd.read_csv(url, sep=";")
        # 3. Limpieza de columnas
        df.columns = df.columns.str.strip()
        # 4. Todo a texto
        df = df.astype(str)
        return df
    except Exception as e:
        return None

# Cargamos ambos conjuntos de datos al inicio
df_curriculo = cargar_datos_csv(SHEET_URL)
df_saberes = cargar_datos_csv(SHEET_SABERES_URL) 
# ==============================================================================

# --- ESTILOS CSS DINÁMICOS (FONDO ANIMADO Y CONTENEDORES) ---
st.markdown(
    """
    <style>
    /* Animación del fondo */
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    /* Contenedores blancos translúcidos para el contenido */
    .block-container {
        padding-top: 2rem;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.92); 
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Botones personalizados */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
    }

    /* Títulos */
    h1, h2, h3 {
        color: #1a237e !important;
    }
    
    /* Estilo para los textos de ayuda laterales */
    .help-text {
        font-size: 0.85rem;
        color: #555;
        border-left: 3px solid #e73c7e;
        padding-left: 10px;
        margin-top: 25px; /* Ajuste para alinear con el input */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNCIONES AUXILIARES ---
def crear_pdf(texto_markdown):
    html_content = markdown.markdown(texto_markdown, extensions=['tables'])
    estilos_css = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: Helvetica, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
        h1 { color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 5px; }
        h2 { color: #283593; margin-top: 20px; }
        h3 { color: #303f9f; }
        p { margin-bottom: 10px; text-align: justify; }
        ul { margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }
        th { background-color: #e8eaf6; color: #1a237e; border: 1px solid #ccc; padding: 8px; text-align: left; }
        td { border: 1px solid #ccc; padding: 8px; }
    </style>
    """
    html_completo = f"<html><head>{estilos_css}</head><body>{html_content}</body></html>"
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_completo, dest=pdf_buffer)
    if pisa_status.err: return None
    return pdf_buffer.getvalue()

def stream_gemini_response(prompt_usuario, placeholder):
    full_text = ""
    stop_updating_ui = False 
    try:
        response = model.generate_content(prompt_usuario, stream=True)
        for chunk in response:
            try:
                if chunk.text:
                    full_text += chunk.text
                    if "___SEPARADOR___" in full_text:
                        if not stop_updating_ui:
                            parte_visible = full_text.split("___SEPARADOR___")[0]
                            placeholder.markdown(parte_visible) 
                            stop_updating_ui = True
                    else:
                        if not stop_updating_ui:
                            placeholder.markdown(full_text + "▌")
                            time.sleep(0.005) 
            except Exception: pass 
        if not stop_updating_ui: placeholder.markdown(full_text)
        return full_text
    except Exception as e:
        placeholder.error(f"Error al contactar con la IA: {e}")
        return None

# ==============================================================================
# 🚀 INTERFAZ DE USUARIO: FLUJO PASO A PASO (WIZARD)
# ==============================================================================

# Encabezado Global
col_logo, col_title = st.columns([1, 6])
with col_title:
    st.title("Aul.IA: Estudio Creativo")
    st.caption("Diseño de Situaciones de Aprendizaje asistido por Inteligencia Artificial")

# ------------------------------------------------------------------------------
# PASO 1: CONTEXTO Y COMPETENCIAS (LOGICA ACTUALIZADA CON DATOS)
# ------------------------------------------------------------------------------
if st.session_state.step == 1:
    
    st.markdown("### 1️⃣ Marco Pedagógico")
    
    col1, col2, col3 = st.columns([1, 6, 1]) 
    with col2:
        st.info("Define las coordenadas pedagógicas de tu situación de aprendizaje.")
        
        # LOGICA DE SELECCIÓN DE CURRICULO
        if df_curriculo is not None:
            # A. CURSO
            cursos_disponibles = sorted(df_curriculo['Curso'].unique().tolist())
            idx_curso = 0
            if st.session_state.input_curso in cursos_disponibles:
                idx_curso = cursos_disponibles.index(st.session_state.input_curso) + 1 # +1 por el placeholder

            sel_curso = st.selectbox(
                "¿A qué curso va dirigido?", 
                ["Selecciona un curso..."] + cursos_disponibles,
                index=idx_curso if st.session_state.input_curso != "Selecciona un curso..." else 0
            )
            st.session_state.input_curso = sel_curso

            # B. CE y CEv (Solo si hay curso)
            if sel_curso != "Selecciona un curso...":
                df_curso_filtrado = df_curriculo[df_curriculo['Curso'] == sel_curso]
                
                # Selección CE
                opciones_ce_visual = df_curso_filtrado.apply(
                    lambda x: f"{x['Codigo_CE']}: {x['Texto_CE']}", axis=1
                ).unique().tolist()
                
                sel_ce_completa = st.selectbox("Competencia Específica (CE):", ["Selecciona una competencia..."] + sorted(opciones_ce_visual))
                
                if sel_ce_completa != "Selecciona una competencia...":
                    codigo_ce_elegido = sel_ce_completa.split(":")[0].strip()
                    # Guardamos el texto limpio en session_state
                    st.session_state.input_ce = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]['Texto_CE'].iloc[0]

                    # Selección CEv
                    df_ce_filtrado = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]
                    opciones_cev_visual = df_ce_filtrado.apply(
                        lambda x: f"{x['Codigo_CEv']}: {x['Texto_CEv']}", axis=1
                    ).unique().tolist()
                    
                    sel_cev_completa = st.selectbox("Criterio de Evaluación (CEv):", ["Selecciona un criterio..."] + sorted(opciones_cev_visual))
                    
                    if sel_cev_completa != "Selecciona un criterio...":
                         codigo_cev = sel_cev_completa.split(":")[0].strip()
                         # Guardamos el texto limpio en session_state
                         st.session_state.input_cev = df_ce_filtrado[df_ce_filtrado['Codigo_CEv'] == codigo_cev]['Texto_CEv'].iloc[0]
                else:
                    st.session_state.input_ce = ""
                    st.session_state.input_cev = ""
            else:
                 st.info("👆 Selecciona primero un curso para ver las competencias.")

        else:
            # FALLBACK MANUAL SI NO HAY DATOS
            st.error("No se pudieron cargar los datos curriculares. Modo manual activado.")
            st.session_state.input_curso = st.selectbox("Curso", ["5º Primaria", "6º Primaria"])
            st.session_state.input_ce = st.text_area("Competencia Específica", value=st.session_state.input_ce)
            st.session_state.input_cev = st.text_area("Criterio de Evaluación", value=st.session_state.input_cev)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón de Continuar (Modificado: YA NO PIDE TEMA AQUÍ)
        if st.button("Continuar a Saberes Básicos ➡️", type="primary"):
            if (st.session_state.input_ce and 
                st.session_state.input_cev and
                st.session_state.input_curso != "Selecciona un curso..."):
                st.session_state.step = 2
                scroll_to_top()
                st.rerun()
            else:
                st.warning("Por favor, completa todos los campos para continuar.")

# ------------------------------------------------------------------------------
# PASO 2: SABERES BÁSICOS (SB) (LOGICA ACTUALIZADA CON DATOS)
# ------------------------------------------------------------------------------
elif st.session_state.step == 2:
    st.markdown("### 2️⃣ Contenidos y Contexto")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"Genial. Ahora, para **{st.session_state.input_curso}**, vamos a definir los saberes y el contexto.")
        
        # ---------------------------------------------------------
        # PARTE A: SABERES BÁSICOS
        # ---------------------------------------------------------
        if df_saberes is not None:
             # 1. BLOQUE
            bloques_disponibles = sorted(df_saberes['Bloque'].unique().tolist())
            
            # Recuperar indice si ya existe
            idx_bloque = 0
            if st.session_state.input_bloque in bloques_disponibles:
                 idx_bloque = bloques_disponibles.index(st.session_state.input_bloque) + 1

            sel_bloque = st.selectbox("Bloque:", ["Selecciona un bloque..."] + bloques_disponibles, index=idx_bloque)
            
            if sel_bloque != "Selecciona un bloque...":
                st.session_state.input_bloque = sel_bloque
                df_bloque_filtrado = df_saberes[df_saberes['Bloque'] == sel_bloque]

                # 2. SUB-APARTADO
                sub_disponibles = sorted(df_bloque_filtrado['Sub-apartado'].unique().tolist())
                idx_sub = 0
                if st.session_state.input_subapartado in sub_disponibles:
                    idx_sub = sub_disponibles.index(st.session_state.input_subapartado) + 1
                
                sel_sub = st.selectbox("Sub-apartado:", ["Selecciona un sub-apartado..."] + sub_disponibles, index=idx_sub)

                if sel_sub != "Selecciona un sub-apartado...":
                    st.session_state.input_subapartado = sel_sub
                    df_sub_filtrado = df_bloque_filtrado[df_bloque_filtrado['Sub-apartado'] == sel_sub]

                    # 3. SABERES
                    # Buscamos la columna correcta
                    col_saberes_name = 'Saberes Básicos (Contenidos Concretos)'
                    if col_saberes_name not in df_saberes.columns:
                        col_candidates = [c for c in df_saberes.columns if c.startswith('Saberes')]
                        if col_candidates: col_saberes_name = col_candidates[0]

                    saberes_disponibles = df_sub_filtrado[col_saberes_name].unique().tolist()
                    idx_sb = 0
                    # Nota: SB puede ser largo, la coincidencia exacta a veces es difícil si el usuario editó
                    if st.session_state.input_sb in saberes_disponibles:
                        idx_sb = saberes_disponibles.index(st.session_state.input_sb) + 1
                    
                    sel_sb = st.selectbox("Saberes Básicos (SB):", ["Selecciona un saber..."] + saberes_disponibles, index=idx_sb)
                    
                    if sel_sb != "Selecciona un saber...":
                        st.session_state.input_sb = sel_sb
            
            # Mostrar lo seleccionado (Confirmación visual)
            if st.session_state.input_sb:
                 st.success(f"Seleccionado: {st.session_state.input_sb}")

        else:
            # FALLBACK MANUAL
            st.error("No se pudieron cargar los datos de Saberes. Modo manual activado.")
            st.session_state.input_bloque = st.text_input("Bloque:", value=st.session_state.input_bloque)
            st.session_state.input_subapartado = st.text_input("Sub-apartado:", value=st.session_state.input_subapartado)
            st.session_state.input_sb = st.text_area("Saberes Básicos (SB):", value=st.session_state.input_sb)
        
        st.markdown("---") # Separador visual

        # ---------------------------------------------------------
        # PARTE B: TEMA / CONTEXTO (MOVIDO AQUÍ)
        # ---------------------------------------------------------
        
        # MENSAJE DE RECOMENDACIÓN
        st.info("Es recomendable que el tema esté relacionado tanto con la Competencia Específica seleccionada como con el Saber Básico establecido")
        
        # INPUT DE TEMA
        st.session_state.input_tema = st.text_input(
            "Tema, Hilo Conductor o Contexto:",
            value=st.session_state.input_tema,
            placeholder="Haz clic aquí para escribir el tema..."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅️ Atrás"):
                st.session_state.step = 1
                scroll_to_top()
                st.rerun()
        with col_next:
            if st.button("✨ Generar Estrategia", type="primary"):
                # VALIDACIÓN: AHORA INCLUYE EL TEMA
                if (st.session_state.input_sb and 
                    st.session_state.input_sb != "Selecciona un saber..." and 
                    st.session_state.input_tema):
                    st.session_state.step = 3
                    scroll_to_top()
                    st.rerun()
                else:
                    st.warning("Por favor, selecciona los Saberes Básicos y escribe un Tema.")

# ------------------------------------------------------------------------------
# PASO 3: PLAN DE FOCO (GENERACIÓN 1)
# ------------------------------------------------------------------------------
elif st.session_state.step == 3:
    st.markdown("### 3️⃣ Brújula Estratégica")
    
    # Variables locales para usar en el prompt
    CURSO = st.session_state.input_curso
    TEMA = st.session_state.input_tema
    CE = st.session_state.input_ce
    CEv = st.session_state.input_cev
    SB = st.session_state.input_sb # Solo usamos los Saberes, ignoramos Bloque y Sub-apartado para la IA
    
    contenedor_plan = st.empty()
    
    # Si ya tenemos plan, lo mostramos, si no, lo generamos
    if not st.session_state.plan_de_foco:
        # ANIMACIÓN
        contenedor_plan.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 200px; flex-direction: column;">
                <div style="font-size: 4rem; animation: balanceo 2s infinite ease-in-out;">🧭</div>
                <h3>Calibrando Brújula Pedagógica...</h3>
            </div>
            <style>@keyframes balanceo { 0% { transform: rotate(0deg); } 25% { transform: rotate(15deg); } 75% { transform: rotate(-15deg); } 100% { transform: rotate(0deg); } }</style>
            """, unsafe_allow_html=True
        )
        
        # PROMPT
        prompt_temporal_plan_foco = f"""
                Rol: Actúa como un Analista Curricular experto y Estratega Pedagógico, especialista en el modelo competencial de la LOMLOE. Eres lógico, riguroso y pedagógico.
                Contexto: Te proporcionaré cinco variables:
                •   {CE} (La Competencia Específica principal)
                •   {CEv} (El Criterio de Evaluación asociado)
                •   {SB} (El/los Saberes Básicos curriculares)
                •   {TEMA} (El contenido concreto o pretexto)
                •   {CURSO} (El grupo de destino)
                Instrucción de Tarea (Crítica): Tu tarea es generar un Plan Estratégico y una Esencia Competencial. Tu salida debe tener dos partes: (1) Un resumen en texto legible para el profesor, y (2) La Esencia Competencial (del Paso 5) como una cadena de texto para el sistema.
                Tarea: Sigue rigurosamente estos 5 pasos para generar el contenido del plan:
                Paso 1 (Análisis Jerárquico por Regla Gramatical): (Cortafuegos: Lee únicamente la {CE} para este paso. IGNORA el {CEv} y el {SB} por completo en esta sección). Aplica la siguiente regla gramatical estricta para clasificar los conceptos de la {CE}:
                Eje Competencial (QUÉ): Lista aquí los verbos de acción principales, los conceptos centrales y el propósito/finalidad. (PISTA: Verbos en infinitivo, sus objetos directos y las cláusulas finales tipo "para...").
                Herramientas de Análisis (CÓMO): Lista aquí los conceptos/métodos. (PISTA: Acciones en gerundio).
                Paso 2 (Análisis de Adecuación al CURSO): Ahora, compara la lista completa de conceptos del Paso 1 (Eje y Herramientas) con el nivel madurativo del {CURSO}. Evalúa explícitamente:
                ¿Qué conceptos son directamente aplicables?
                ¿Qué conceptos presentan una alta complejidad cognitiva y requerirán una adaptación?
                Paso 3 (Declaración del Foco Realista): Basándote en el análisis de adecuación del Paso 2, declara el foco realista para esta SA.
                Foco en el Eje (QUÉ): Declara cómo se abordará el Eje (incluyendo el propósito/finalidad).
                Foco en las Herramientas (CÓMO): Selecciona las "Herramientas de Análisis" más relevantes para el {TEMA} y el {CURSO}.
                Paso 4 (Declaración de Renuncia Estratégica): Basándote en los pasos 2 y 3, declara explícitamente qué conceptos (del "Eje" o de las "Herramientas") quedan definitivamente fuera de foco. Justifica esta renuncia basándote en tu análisis del Paso 2.
                Paso 5 (Síntesis de Esencia Competencial - {{EsCE}}): Tu tarea es generar la Esencia Competencial ({{EsCE}}). Sigue estas reglas estrictas:
                Cortafuegos de Fuentes (Crítico): Para este paso, debes basarte única y exclusivamente en el texto que tú mismo has generado en el "paso3_focoRealista".
                Cortafuegos de Omisión (Crítico): Tienes explícitamente prohibido usar la {CE} original, el {CEv} o el texto del "paso4_renunciaEstrategica" para construir esta esencia.
                Instrucción de Formato (Regla Gramatical): Debes sintetizar los elementos del "Paso 3" en un único párrafo de texto que siga la misma estructura gramatical de una Competencia Específica (Infinitivo -> Gerundio -> Finalidad).

                Formato de Salida Obligatorio: Tu respuesta debe tener dos partes separadas por un delimitador único. Sigue este formato rigurosamente:
                PARTE 1: Resumen para el Profesor (Texto) Genera aquí un resumen en prosa (usando Markdown para títulos y listas) destinado al profesor. Este resumen debe presentar de forma clara los resultados de tu análisis (Pasos 2, 3 y 4) para que el docente pueda validarlo.
                Debe incluir un título (ej. ### 💡 Propuesta de Foco Estratégico).
                Debe presentar el Análisis de Adecuación (del Paso 2).
                Debe presentar el Foco Realista (del Paso 3).
                Debe presentar la Renuncia Estratégica (del Paso 4).
                (No incluyas el Paso 1 ni el 5 en este resumen, ya que son abstractos o técnicos).
                ___SEPARADOR___
                PARTE 2: Tiene que contener la misma información que la PARTE 1 pero siendo un objeto JSON válido. El objeto JSON debe seguir este esquema:
                JSON
                {{
                "focoEstrategico": {{
                    "paso1_analisisJerarquico": {{
                    "ejeCompetencial_QUE": [
                        "Extraer aquí el primer concepto del Eje...",
                        "Extraer aquí el segundo concepto del Eje...",
                        "Extraer aquí el propósito/finalidad..."
                    ],
                    "herramientasAnalisis_COMO": [
                        "Extraer aquí la primera herramienta...",
                        "Extraer aquí la segunda herramienta..."
                    ]
                    }},
                    "paso2_analisisAdecuacion": {{
                    "conceptosAplicables": "Análisis de los conceptos aplicables...",
                    "conceptosComplejos": "Análisis de los conceptos que requieren adaptación..."
                    }},
                    "paso3_focoRealista": {{
                    "focoEje_QUE": "Declaración del foco en el Eje y su finalidad...",
                    "focoHerramientas_COMO": "Declaración del foco en las Herramientas..."
                    }},
                    "paso4_renunciaEstrategica": {{
                    "renuncia": "Conceptos que quedan fuera de foco...",
                    "justificacion": "Justificación pedagógica de la renuncia..."
                    }}
                }},
                "esenciaCompetencial_EsCE": "El texto de la Competencia Específica reconstruido según las reglas del Paso 5."
                }}"""
        
        respuesta_ia = stream_gemini_response(prompt_temporal_plan_foco, contenedor_plan)
        
        if respuesta_ia:
            if "___SEPARADOR___" in respuesta_ia:
                partes = respuesta_ia.split("___SEPARADOR___")
                st.session_state.plan_de_foco = partes[0].strip()
                st.session_state.plan_json = partes[1].strip()
                st.rerun() 
            else:
                st.session_state.plan_de_foco = respuesta_ia
                st.session_state.plan_json = respuesta_ia

    # Mostrar el resultado si ya existe
    if st.session_state.plan_de_foco:
        contenedor_plan.markdown(st.session_state.plan_de_foco)
        
        st.divider()
        col_ok, col_ko = st.columns([2, 1])
        with col_ok:
            if st.button("✅ Estrategia Correcta: Crear Situación de Aprendizaje", type="primary"):
                st.session_state.step = 4
                scroll_to_top()
                st.rerun()
        with col_ko:
            if st.button("🔄 Reiniciar Análisis"):
                st.session_state.plan_de_foco = None
                st.rerun()

# ------------------------------------------------------------------------------
# PASO 4: GENERACIÓN FINAL Y EDICIÓN
# ------------------------------------------------------------------------------
elif st.session_state.step == 4:
    st.markdown("### 4️⃣ Situación de Aprendizaje")
    
    contenedor_final = st.empty()
    
    # Recuperamos variables
    CURSO = st.session_state.input_curso
    TEMA = st.session_state.input_tema
    CEv = st.session_state.input_cev
    SB = st.session_state.input_sb # Solo usamos los Saberes, ignoramos Bloque y Sub-apartado para la IA
    json_recuperado = st.session_state.plan_json
    
    # Lógica de generación automática al entrar en este paso
    if not st.session_state.sa_generada:
        contenedor_final.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 200px; flex-direction: column;">
                <div style="font-size: 4rem; animation: latido 1.5s infinite ease-in-out;">🧠</div>
                <h3>El Artesano Digital está pensando...</h3>
                <p>Conectando saberes, diseñando el contexto y estructurando la rúbrica.</p>
            </div>
            <style>@keyframes latido { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.7; } 100% { transform: scale(1); opacity: 1; } }</style>
            """, unsafe_allow_html=True
        )
        
        PROMPT_FABRICACION = f"""
                Rol: Actúa como un experto Diseñador Instruccional y Pedagogo especialista en la creación de Situaciones de Aprendizaje (SA) competenciales según la LOMLOE. Eres creativo, preciso y riguroso.
                
                Contexto: Te proporcionaré variables de entrada definidas por el usuario y un plan estratégico JSON.
                
                VARIABLES DEL USUARIO:
                - Criterio de Evaluación: {CEv}
                - Saberes Básicos: {SB}
                - Tema/Contenido: {TEMA}
                - Curso: {CURSO}
                
                PLAN ESTRATÉGICO (JSON):
                {json_recuperado}
                
                Instrucción de Tarea (Crítica): Tu trabajo es generar el contenido pedagógico de la Situación de Aprendizaje. Tu respuesta debe contener ÚNICAMENTE las secciones 1, 2, 3,  4 y 5.
                
                Tarea: Genera la Situación de Aprendizaje siguiendo estas instrucciones paso a paso:

                1. Título de la Situación de Aprendizaje
                (Genera un título atractivo que combine el {TEMA} y el desafío).

                2. Enfoque Curricular 
                - Saberes Básicos Movilizados: (Confirma y lista los {SB} proporcionados).
                - Conexiones Curriculares: (Menciona brevemente si la SA trabaja de forma secundaria otras competencias o materias).

                3. Objetivos Competenciales (OC)
                Define 1 o 2 Objetivos Competenciales. Es fundamental que empiecen con un verbo de acción y sean evaluables.
                
                *** IMPORTANTE ***
                Para redactar estos objetivos, NO uses la competencia genérica. DEBES USAR la "esenciaCompetencial_EsCE" que encontrarás dentro del JSON de arriba. Esa es tu brújula.
                
                - Instrucción de Alineación: Cada OC debe ser una fusión de esa "esenciaCompetencial_EsCE" con los {SB} y el {TEMA}.
                - Instrucción de Adecuación: La formulación debe ser cognitivamente adecuada y comprensible para el {CURSO}. 

                4. Situación de Aprendizaje (SA)
                - Contexto y Desafío: Describe un contexto del mundo real (basado en el {TEMA}) que sea relevante para el {CURSO}.
                - Producto Final / Actuación: Describe un producto tangible o actuación que el alumnado debe crear y que esté alineado con los OCs. El producto final debe ser alcanzable y adecuado para la autonomía y las destrezas esperadas en el {CURSO}.
                - Secuenciación de Tareas: Describe las fases clave de la SA, incluyendo agrupamientos (colaborativos) y una fase final de metacognición. Las tareas deben estar diseñadas para desarrollar los OCs.

                5. Rúbrica de Evaluación
                Instrucción de Formato: Crea una tabla de rúbrica.
                - Filas: Los OCs definidos en la Sección 3.
                - Columnas: Niveles de desempeño.
                
                Instrucción de Niveles: Los niveles deben describir actuaciones observables y específicas de la SA, con una progresión clara de desempeño realista y adecuada para el {CURSO}.
                
                - Nivel 1 (En inicio): Actuación incorrecta, muy incompleta o basada en ideas previas erróneas.
                - Nivel 2 (En desarrollo): Actuación correcta pero simple, parcial, o sin la justificación/precisión requerida.
                - Nivel 3 (Avanzado): Actuación correcta, completa y justificada, ceñida a la tarea.
                - Nivel 4 (Experto): Actuación ideal.
                
                Restricción de Adecuación: Todos los descriptores, especialmente el Nivel 4, deben ser observables y alcanzables por un alumno estándar del {CURSO}.
                
                | Objetivo Competencial (OC) | Nivel 1: En inicio | Nivel 2: En desarrollo | Nivel 3: Avanzado | Nivel 4: Experto |
                | :--- | :--- | :--- | :--- | :--- |
                | (OC 1) | (Descriptor N1) | (Descriptor N2) | (Descriptor N3) | (Descriptor N4) |
                | (OC 2) | (Descriptor N1) | (Descriptor N2) | (Descriptor N3) | (Descriptor N4) |

                """
        
        resultado_sa = stream_gemini_response(PROMPT_FABRICACION, contenedor_final)
        
        if resultado_sa:
            st.session_state.sa_generada = resultado_sa
            st.session_state.editor_sa = resultado_sa
            st.rerun()

    # VISUALIZACIÓN DE RESULTADOS
    if st.session_state.sa_generada:
        with contenedor_final.container():
            tab_vista, tab_editor = st.tabs(["👀 Vista Previa", "✏️ Editor"])

            with tab_vista:
                st.markdown(st.session_state.sa_generada)

            with tab_editor:
                sa_final_editada = st.text_area(
                    "Edita tu Situación de Aprendizaje:",
                    height=600, 
                    value=st.session_state.sa_generada, 
                    key="editor_sa_area", 
                    label_visibility="collapsed" 
                )
                if sa_final_editada != st.session_state.sa_generada:
                     st.session_state.sa_generada = sa_final_editada

        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
             st.download_button(
                label="📥 Descargar Markdown",
                data=st.session_state.sa_generada,
                file_name="situacion_aprendizaje.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
            pdf_bytes = crear_pdf(st.session_state.sa_generada)
            if pdf_bytes:
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name="situacion_aprendizaje.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        if st.button("🔄 Crear Nueva Situación (Reiniciar)"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()