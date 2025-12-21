import streamlit as st
import google.generativeai as genai
import time
import markdown 
from xhtml2pdf import pisa 
import io 
import pandas as pd 
import os 
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (ESTO DEBE IR SIEMPRE PRIMERO) ---
st.set_page_config(layout="wide", page_title="Aul.IA - Debug Mode") 

# ==============================================================================
# 🕵️‍♂️ ZONA DE DIAGNÓSTICO DE ARCHIVOS (PARA VER EL ERROR Y MODELOS)
# ==============================================================================
with st.expander("🕵️‍♂️ DIAGNÓSTICO DE ARCHIVOS (Clic para abrir)", expanded=True):
    st.write(f"📂 **Carpeta desde donde se ejecuta Python:** `{os.getcwd()}`")
    
    archivos_raiz = os.listdir()
    st.write(f"👀 **Archivos que veo en esta carpeta:** {archivos_raiz}")
    
    # Verificación específica de carpetas y secrets
    if os.path.exists(".streamlit"):
        st.success("✅ La carpeta `.streamlit` EXISTE.")
        archivos_dentro = os.listdir(".streamlit")
        st.write(f"   ↳ Dentro de .streamlit veo: {archivos_dentro}")
        
        if "secrets.toml" in archivos_dentro:
            st.success("✅ El archivo `secrets.toml` EXISTE dentro de la carpeta.")
        else:
            st.error("❌ La carpeta existe, pero NO veo `secrets.toml` dentro.")
    else:
        st.error("❌ NO encuentro la carpeta `.streamlit` en la ruta actual.")

    # Verificación de claves en st.secrets
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            st.success("🔓 ¡Streamlit ha podido leer los secretos correctamente!")
        else:
            st.warning("⚠️ El archivo existe pero no encuentro la clave GOOGLE_API_KEY dentro.")
            
        if "gcp_service_account" in st.secrets:
             st.success("🔓 Credenciales de Google Sheets encontradas.")
             st.info(f"📧 **Email del Robot:** `{st.secrets['gcp_service_account']['client_email']}` (Asegúrate de compartir la hoja con este email)")
        else:
             st.error("❌ Falta la sección [gcp_service_account] en secrets.")
             
    except Exception as e:
        st.error(f"💀 Error fatal intentando leer st.secrets: {e}")

    # --- NUEVA LÓGICA: LISTAR MODELOS DISPONIBLES ---
    st.markdown("---")
    st.write("🤖 **Modelos de IA Disponibles para tu API Key:**")
    
    try:
        # Configuramos la API temporalmente para hacer la consulta
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            
            modelos_disponibles_api = []
            # Listamos los modelos y filtramos los que sirven para generar texto
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles_api.append(m.name)
            
            st.success(f"✅ Conexión exitosa con Google AI. He encontrado {len(modelos_disponibles_api)} modelos compatibles.")
            st.code(modelos_disponibles_api)
            
            # Pequeña ayuda visual para elegir el mejor
            if 'models/gemini-1.5-pro' in modelos_disponibles_api:
                st.caption("🌟 Recomendación: Veo que tienes acceso a `models/gemini-1.5-pro`. Es el más recomendado.")
        else:
            st.warning("⚠️ No puedo buscar modelos sin la GOOGLE_API_KEY.")
            
    except Exception as e:
        st.error(f"❌ Error al intentar conectar con Google AI para listar modelos: {e}")

st.divider()
# ==============================================================================

# Cargar la API Key
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except FileNotFoundError:
    st.error("No se encontró el archivo secrets.toml.")
except KeyError:
    st.error("No se encontró la GOOGLE_API_KEY en secrets.toml.")

# --- LISTA DE MODELOS PERMITIDOS ---
MODELOS_PERMITIDOS = [
    'models/gemini-2.5-flash', 'models/gemini-2.5-pro', 'models/gemini-2.0-flash-exp', 
    'models/gemini-2.0-flash', 'models/gemini-2.0-flash-001', 'models/gemini-2.0-flash-lite-001', 
    'models/gemini-2.0-flash-lite', 'models/gemini-2.0-flash-lite-preview-02-05', 
    'models/gemini-2.0-flash-lite-preview', 'models/gemini-2.0-pro-exp', 
    'models/gemini-2.0-pro-exp-02-05', 'models/gemini-exp-1206', 
    'models/gemini-2.5-flash-preview-tts', 'models/gemini-2.5-pro-preview-tts', 
    'models/gemma-3-1b-it', 'models/gemma-3-4b-it', 'models/gemma-3-12b-it', 
    'models/gemma-3-27b-it', 'models/gemma-3n-e4b-it', 'models/gemma-3n-e2b-it', 
    'models/gemini-flash-latest', 'models/gemini-flash-lite-latest', 
    'models/gemini-pro-latest', 'models/gemini-2.5-flash-lite', 
    'models/gemini-2.5-flash-image-preview', 'models/gemini-2.5-flash-image', 
    'models/gemini-2.5-flash-preview-09-2025', 'models/gemini-2.5-flash-lite-preview-09-2025', 
    'models/gemini-3-pro-preview', 'models/gemini-3-pro-image-preview', 
    'models/nano-banana-pro-preview', 'models/gemini-robotics-er-1.5-preview', 
    'models/gemini-2.5-computer-use-preview-10-2025'
]

# Modelo por defecto
DEFAULT_MODEL = 'models/gemini-2.5-pro' 

# ==============================================================================
# 📊 LÓGICA DE REGISTRO EN GOOGLE SHEETS
# ==============================================================================
SHEET_NAME_REGISTRO = "Registro_Aul.IA" # Asegúrate de que tu hoja en Drive se llame así

def conectar_google_sheets():
    """Conecta con Google Sheets usando las credenciales de secrets.toml"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" not in st.secrets:
            st.error("Falta la sección [gcp_service_account] en secrets.toml")
            return None

        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Corrección de formato para la clave privada
        if "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error conectando a Sheets: {e}")
        return None

def registrar_actividad(datos):
    """Escribe una fila en Google Sheets e informa detalladamente del error"""
    client = conectar_google_sheets()
    if client:
        try:
            sheet = client.open(SHEET_NAME_REGISTRO).sheet1
            
            # Convertimos explícitamente cada elemento a string
            datos_seguros = [str(dato) for dato in datos]
            
            # [ANCLAJE DE RANGO REALIZADO AQUÍ]
            sheet.append_row(datos_seguros, table_range='A1', value_input_option='USER_ENTERED')
            return True
            
        except Exception as e:
            # --- ZONA DE DIAGNÓSTICO DE ERROR ---
            st.error("❌ Error CRÍTICO al intentar escribir en Google Sheets.")
            
            st.markdown(f"**Mensaje simple del error:** `{e}`")
            st.markdown(f"**Tipo de error:** `{type(e).__name__}`")
            
            if hasattr(e, 'response'):
                st.info("📡 He encontrado una respuesta del servidor dentro del error. Aquí está su contenido:")
                try:
                    contenido_respuesta = e.response.text
                    st.code(contenido_respuesta) 
                except:
                    st.warning("El error tiene respuesta, pero no pude leer su texto.")
            else:
                st.warning("El objeto de error no contiene una respuesta HTTP legible.")
                
            return False
    return False

# ==============================================================================
# LOGICA DE DATOS 1: CURRÍCULO (Curso -> CE -> CEv)
# ==============================================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRp8yJQGCVyGEbrNn0zgEzy5-iLxhnS4fpA7oV6yA5bPA95wW6V0waRm78c6rea_A/pub?gid=650080582&single=true&output=csv" 

# ==============================================================================
# LOGICA DE DATOS 2: SABERES (Bloque -> Sub-apartado -> Saberes)
# ==============================================================================
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

# Cargamos ambos conjuntos de datos
df_curriculo = cargar_datos_csv(SHEET_URL)
df_saberes = cargar_datos_csv(SHEET_SABERES_URL) 
# ==============================================================================

# Función para generar el PDF
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
    
    if pisa_status.err:
        return None
    
    return pdf_buffer.getvalue()

def stream_gemini_response(prompt_usuario, placeholder, model_name):
    full_text = ""
    stop_updating_ui = False 

    # Instanciamos el modelo aquí con el nombre seleccionado
    local_model = genai.GenerativeModel(model_name)

    try:
        response = local_model.generate_content(prompt_usuario, stream=True)
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
            except Exception:
                pass 
        
        if not stop_updating_ui:
            placeholder.markdown(full_text)
            
        return full_text
        
    except Exception as e:
        placeholder.error(f"Error al contactar con la IA ({model_name}): {e}")
        return None

# --- ESTILOS Y FONDO ---
background_color = "#F5F7FA" 
svg_stroke_color = "#DEE2E6" 
st.markdown(
    f"""
    <style>
    body {{ background-color: {background_color}; position: relative; min-height: 100vh; }}
    .stApp {{ background-color: transparent; }}
    [data-testid="stAppViewContainer"] > .main {{ background-color: transparent; }}
    .background-svg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}
    .stroke-style {{ stroke: {svg_stroke_color}; stroke-width: 1px; fill: none; }}
    </style>
    <svg class='background-svg' viewBox='0 0 1000 1000' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>
        <path d='M100 100 L250 150 L300 300 L150 400 L50 250 Z' class='stroke-style'/>
    </svg>
    """,
    unsafe_allow_html=True
)

# --- INICIALIZACIÓN DE LA MEMORIA ---
if 'plan_de_foco' not in st.session_state: st.session_state.plan_de_foco = None 
if 'plan_json' not in st.session_state: st.session_state.plan_json = None    
if 'sa_generada' not in st.session_state: st.session_state.sa_generada = None 
if 'editor_sa' not in st.session_state: st.session_state.editor_sa = "Pulsa 'Crear Situación de Aprendizaje' arriba para generar el contenido."

# --- VARIABLES DE ESTADO PARA REGISTRO (ANALÍTICA) ---
if 'time_focus' not in st.session_state: st.session_state.time_focus = 0.0
if 'time_sa' not in st.session_state: st.session_state.time_sa = 0.0
if 'data_logged' not in st.session_state: st.session_state.data_logged = False

# [NUEVO] Inicialización de la memoria "Snapshot" para persistencia
if 'contexto_generacion' not in st.session_state: st.session_state.contexto_generacion = {}

# [NUEVO] Variables para guardar qué modelo se usó en cada paso
if 'modelo_foco_usado' not in st.session_state: st.session_state.modelo_foco_usado = ""
if 'modelo_sa_usado' not in st.session_state: st.session_state.modelo_sa_usado = ""

# --- TÍTULO Y PANELES ---
st.title("Aul.IA: Creación de Situaciones de Aprendizaje")
col1, col2 = st.columns([1, 2])

# --- PANEL DERECHO (INPUTS) ---
with col2:
    st.subheader("Paso 1: Define tus variables")
    
    # [NOTA] He eliminado el selector de modelo general de aquí. Se seleccionará en el Paso 3.
    
    # ======================================================================
    # CASCADA 1: CURSO -> CE -> CEv (MODIFICADO PARA NO AUTOCOMPLETAR)
    # ======================================================================
    if df_curriculo is not None:
        try:
            cursos_disponibles = sorted(df_curriculo['Curso'].unique().tolist())
            lista_cursos = ["Selecciona un curso..."] + cursos_disponibles
            CURSO = st.selectbox("Elige el curso:", lista_cursos)
        except Exception:
            CURSO = "Selecciona un curso..."
        
        CE = ""
        CEv = ""

        if CURSO != "Selecciona un curso...":
            df_curso_filtrado = df_curriculo[df_curriculo['Curso'] == CURSO]

            # Selección CE con Placeholder
            opciones_ce_visual = df_curso_filtrado.apply(
                lambda x: f"{x['Codigo_CE']}: {x['Texto_CE']}", axis=1
            ).unique().tolist()
            
            # Añadimos la opción por defecto al principio
            lista_ce = ["Selecciona una competencia..."] + sorted(opciones_ce_visual)
            ce_seleccionada_completa = st.selectbox("Competencia Específica (CE):", lista_ce)
            
            # Solo procedemos si el usuario ha elegido una competencia válida
            if ce_seleccionada_completa != "Selecciona una competencia...":
                codigo_ce_elegido = ce_seleccionada_completa.split(":")[0].strip()
                CE = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]['Texto_CE'].iloc[0]

                # Selección CEv con Placeholder
                df_ce_filtrado = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]
                opciones_cev_visual = df_ce_filtrado.apply(
                    lambda x: f"{x['Codigo_CEv']}: {x['Texto_CEv']}", axis=1
                ).unique().tolist()
                
                # Añadimos la opción por defecto al principio
                lista_cev = ["Selecciona un criterio..."] + sorted(opciones_cev_visual)
                cev_seleccionado_completo = st.selectbox("Criterio de Evaluación (CEv):", lista_cev)
                
                # Solo procedemos si el usuario ha elegido un criterio válido
                if cev_seleccionado_completo != "Selecciona un criterio...":
                    codigo_cev = cev_seleccionado_completo.split(":")[0].strip()
                    CEv = df_ce_filtrado[df_ce_filtrado['Codigo_CEv'] == codigo_cev]['Texto_CEv'].iloc[0]

    else:
        st.error("⚠️ Error: Datos Curriculares no cargados.")
        CURSO = st.selectbox("Elige el curso:", ("5º Primaria", "6º Primaria"))
        CE = st.text_input("Competencia Específica (CE):")
        CEv = st.text_input("Criterio de Evaluación (CEv):")

    st.markdown("---") # Separador visual

    # ======================================================================
    # CASCADA 2: BLOQUE -> SUB-APARTADO -> SABERES (LÓGICA ACTUALIZADA)
    # ======================================================================
    # Inicializamos variables vacías por defecto
    BLOQUE = ""
    SUB_APARTADO = ""
    SB = ""

    if df_saberes is not None:
        try:
            # 1. SELECCIÓN DE BLOQUE
            bloques_disponibles = sorted(df_saberes['Bloque'].unique().tolist())
            lista_bloques = ["Selecciona un bloque..."] + bloques_disponibles
            bloque_sel_raw = st.selectbox("Bloque:", lista_bloques)

            # Si el usuario selecciona un bloque válido, procedemos
            if bloque_sel_raw != "Selecciona un bloque...":
                BLOQUE = bloque_sel_raw
                df_bloque_filtrado = df_saberes[df_saberes['Bloque'] == BLOQUE]

                # 2. SELECCIÓN DE SUB-APARTADO
                sub_disponibles = sorted(df_bloque_filtrado['Sub-apartado'].unique().tolist())
                lista_sub = ["Selecciona un sub-apartado..."] + sub_disponibles
                sub_sel_raw = st.selectbox("Sub-apartado:", lista_sub)
                
                # Si el usuario selecciona un sub-apartado válido, procedemos
                if sub_sel_raw != "Selecciona un sub-apartado...":
                    SUB_APARTADO = sub_sel_raw
                    df_sub_filtrado = df_bloque_filtrado[df_bloque_filtrado['Sub-apartado'] == SUB_APARTADO]

                    # 3. SELECCIÓN DE SABERES BÁSICOS
                    # Nombre de la columna (seguridad)
                    col_saberes_name = 'Saberes Básicos (Contenidos Concretos)'
                    if col_saberes_name not in df_saberes.columns:
                        col_candidates = [c for c in df_saberes.columns if c.startswith('Saberes')]
                        if col_candidates:
                            col_saberes_name = col_candidates[0]
                    
                    saberes_disponibles = df_sub_filtrado[col_saberes_name].unique().tolist()
                    lista_sb = ["Selecciona un saber..."] + saberes_disponibles
                    sb_sel_raw = st.selectbox("Saberes Básicos (SB):", lista_sb)

                    # Si el usuario selecciona un saber válido, asignamos la variable
                    if sb_sel_raw != "Selecciona un saber...":
                        SB = sb_sel_raw
        
        except Exception as e:
            st.error(f"Error en la lógica de Saberes: {e}")
            bloque_sel_raw = "Selecciona un bloque..."
    
    else:
        # Modo Manual si no hay enlace o falla la carga
        if "PON_AQUI" in SHEET_SABERES_URL:
            st.warning("⚠️ Debes configurar el enlace SHEET_SABERES_URL en el código para activar los desplegables de Saberes.")
        else:
            st.error("⚠️ No se pudo cargar la tabla de Saberes.")
            
        col_bloque, col_sub = st.columns(2)
        with col_bloque:
            BLOQUE = st.text_input("Bloque:", placeholder="Ej: A. Retos del mundo actual")
        with col_sub:
            SUB_APARTADO = st.text_input("Sub-apartado:", placeholder="Ej: Hábitos de vida saludable")
        SB = st.text_area("Saberes Básicos (SB):", height=100)

    # 4. TEMA (MOVIDO AL PASO 2 según tu anterior petición)
    st.info("Es recomendable que el tema esté relacionado tanto con la Competencia Específica seleccionada como con el Saber Básico establecido")
    TEMA = st.text_input("Contenido concreto o pretexto:", placeholder="Haz clic aquí para escribir el tema...")


# --- PANEL IZQUIERDO (PLAN DE FOCO) ---
with col1:
    st.subheader("Paso 2: Plan de Foco Estratégico")
    contenedor_plan = st.empty()
    if st.session_state.plan_de_foco:
        contenedor_plan.success(st.session_state.plan_de_foco) 
    else:
        contenedor_plan.info("El Plan de Foco generado por la IA aparecerá aquí...")

# --- ZONA DE BOTONES ---
st.divider() 
st.subheader("Paso 3: Generación")

col_btn1, col_btn2 = st.columns(2)

# --- CONFIGURACIÓN DE ÍNDICE POR DEFECTO ---
try:
    default_index = MODELOS_PERMITIDOS.index(DEFAULT_MODEL)
except ValueError:
    default_index = 0

# --- BOTÓN 1: Generar Plan ---
with col_btn1:
    # [NUEVO] Selector específico para el Plan
    modelo_plan_seleccionado = st.selectbox(
        "🧠 IA para el Plan:", 
        MODELOS_PERMITIDOS, 
        index=default_index,
        key="sel_modelo_plan"
    )

    if st.button("Generar Plan de Foco Estratégico", use_container_width=True):
        # Validación
        if not CE or not CEv or not TEMA or not SB or not CURSO or CURSO == "Selecciona un curso..." or not BLOQUE or not SUB_APARTADO:
            st.error("⚠️ Por favor, rellena todos los campos.")
        else:
            # ==============================================================================
            #   🔵  ANIMACIÓN: BRÚJULA ESTRATÉGICA   🔵
            # ==============================================================================
            contenedor_plan.markdown(
                """
                <style>
                    @keyframes balanceo {
                        0% { transform: rotate(0deg); }
                        25% { transform: rotate(15deg); }
                        50% { transform: rotate(0deg); }
                        75% { transform: rotate(-15deg); }
                        100% { transform: rotate(0deg); }
                    }
                    .strategy-box {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 2rem;
                        background-color: #e3f2fd;
                        border-radius: 12px;
                        border: 2px solid #90caf9;
                        margin-bottom: 1rem;
                        color: #0d47a1;
                    }
                    .strategy-emoji {
                        font-size: 3.5rem;
                        margin-right: 1.5rem;
                        animation: balanceo 2s infinite ease-in-out;
                        filter: drop-shadow(0 2px 5px rgba(0,0,0,0.1));
                    }
                    .strategy-text h4 {
                        margin: 0;
                        color: #1565c0;
                        font-weight: 700;
                    }
                    .strategy-text p {
                        margin: 0.3rem 0 0 0;
                        color: #546e7a;
                        font-size: 0.9rem;
                    }
                </style>
                <div class="strategy-box">
                    <div class="strategy-emoji">🧭</div>
                    <div class="strategy-text">
                        <h4>Calibrando Brújula Pedagógica...</h4>
                        <p>Analizando jerarquía competencial y alineando objetivos.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # ==============================================================================
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
            
            # --- MEDICIÓN DE TIEMPO (FOCO) ---
            inicio_foco = time.time()
            # Pasamos el modelo seleccionado a la función de streaming
            respuesta_ia = stream_gemini_response(prompt_temporal_plan_foco, contenedor_plan, modelo_plan_seleccionado)
            fin_foco = time.time()
            st.session_state.time_focus = round(fin_foco - inicio_foco, 2)
            # --------------------------------

            if respuesta_ia:
                if "___SEPARADOR___" in respuesta_ia:
                    partes = respuesta_ia.split("___SEPARADOR___")
                    st.session_state.plan_de_foco = partes[0].strip()
                    st.session_state.plan_json = partes[1].strip()
                    # [NUEVO] Guardamos el modelo usado en sesión
                    st.session_state.modelo_foco_usado = modelo_plan_seleccionado
                    st.session_state.data_logged = False # Resetear log si se genera nuevo plan
                    st.rerun()
                else:
                    st.warning("La IA no generó el separador. Mostrando respuesta completa.")
                    st.session_state.plan_de_foco = respuesta_ia
                    st.session_state.plan_json = respuesta_ia 
                    # [NUEVO] Guardamos el modelo usado en sesión
                    st.session_state.modelo_foco_usado = modelo_plan_seleccionado
                    st.session_state.data_logged = False

# --- BOTÓN 2: Solo dibujamos el botón (La lógica va abajo) ---
with col_btn2:
    # [NUEVO] Selector específico para la SA
    modelo_sa_seleccionado = st.selectbox(
        "🧠 IA para la SA:", 
        MODELOS_PERMITIDOS, 
        index=default_index,
        key="sel_modelo_sa"
    )
    
    # Capturamos el clic del usuario en una variable
    btn_crear_sa = st.button("Crear Situación de Aprendizaje", use_container_width=True, type="primary")

# --- PASO 4: SITUACIÓN DE APRENDIZAJE GENERADA ---
st.markdown("---") 
st.subheader("Paso 4: Situación de Aprendizaje Generada")

# [CLAVE] Creamos el contenedor AQUÍ, en la posición final.
contenedor_paso_4 = st.empty()

# LÓGICA DE GENERACIÓN (Al pulsar Botón 2)
if btn_crear_sa:
    if not st.session_state.plan_json:
        st.error("⚠️ Primero debes generar el Plan de Foco (Botón 1).")
    else:
        # Recuperamos JSON
        json_recuperado = st.session_state.plan_json
        
        # Animación de espera
        contenedor_paso_4.markdown(
            """
            <style>
                @keyframes latido {
                    0% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.1); opacity: 0.7; }
                    100% { transform: scale(1); opacity: 1; }
                }
                .thinking-box {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 3rem 2rem;
                    background-color: #f8f9fa;
                    border-radius: 12px;
                    border: 2px dashed #dee2e6;
                    margin-bottom: 1rem;
                }
                .thinking-emoji {
                    font-size: 4rem;
                    margin-right: 1.5rem;
                    animation: latido 1.5s infinite ease-in-out;
                }
                .thinking-text h3 {
                    margin: 0;
                    color: #2c3e50;
                }
                .thinking-text p {
                    margin: 0.5rem 0 0 0;
                    color: #7f8c8d;
                    font-style: italic;
                }
            </style>
            <div class="thinking-box">
                <div class="thinking-emoji">🧠</div>
                <div class="thinking-text">
                    <h3>El Artesano Digital está pensando...</h3>
                    <p>Conectando saberes, diseñando el contexto y estructurando la rúbrica.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Definición del Prompt (INTACTO)
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
        
        # --- MEDICIÓN DE TIEMPO (SA) ---
        inicio_sa = time.time()
        
        # [STREAMING] Escribimos directamente en el contenedor del paso 4
        # Pasamos el modelo seleccionado a la función de streaming
        resultado_sa = stream_gemini_response(PROMPT_FABRICACION, contenedor_paso_4, modelo_sa_seleccionado)
        
        fin_sa = time.time()
        st.session_state.time_sa = round(fin_sa - inicio_sa, 2) # Guardar tiempo

        if resultado_sa:
            st.session_state.sa_generada = resultado_sa
            st.session_state.editor_sa = resultado_sa 
            # [NUEVO] Guardamos el modelo usado en sesión
            st.session_state.modelo_sa_usado = modelo_sa_seleccionado
            
            # [CAMBIO IMPORTANTE] CAPTURA DEL SNAPSHOT DE VARIABLES
            # Guardamos el estado exacto con el que se generó la SA, incluyendo AMBOS modelos
            st.session_state.contexto_generacion = {
                "curso": CURSO,
                "ce": CE,
                "cev": CEv,
                "bloque": BLOQUE,
                "sub": SUB_APARTADO,
                "sb": SB,
                "tema": TEMA,
                "modelo_plan": st.session_state.modelo_foco_usado, # Modelo del Paso 1
                "modelo_sa": st.session_state.modelo_sa_usado      # Modelo del Paso 2
            }
            
            st.rerun()

# LÓGICA DE VISUALIZACIÓN (ORDEN INVERTIDO)
if st.session_state.sa_generada:
    with contenedor_paso_4.container():
        # [CAMBIO] Primero Vista Previa, Segundo Editor
        tab_vista, tab_editor = st.tabs(["👀 Vista Previa (Documento Final)", "✏️ Editor (Código)"])

        with tab_vista:
            st.info("Así es como se verá tu documento al exportarlo o imprimirlo.")
            st.markdown(st.session_state.sa_generada)

        with tab_editor:
            st.caption("Aquí puedes editar el texto. Las tablas se verán como 'código' con barras vertical (|).")
            sa_final_editada = st.text_area(
                "Edita tu Situación de Aprendizaje:",
                st.session_state.sa_generada,
                height=600, 
                key="editor_sa_area", # Clave cambiada para evitar conflictos
                label_visibility="collapsed" 
            )
            # Actualizamos la memoria si el usuario edita
            if sa_final_editada != st.session_state.sa_generada:
                st.session_state.sa_generada = sa_final_editada

else:
    if not btn_crear_sa:
        contenedor_paso_4.info("Pulsa 'Crear Situación de Aprendizaje' arriba para generar el contenido.")

# ==============================================================================
# ZONA DE DESCARGA Y ACCIONES FINALES
# ==============================================================================
mensaje_inicial = "Pulsa 'Crear Situación de Aprendizaje' arriba para generar el contenido."

if st.session_state.sa_generada and st.session_state.sa_generada != mensaje_inicial:
    st.markdown("---")
    st.subheader("Paso 5: Exportar y Registrar")
    
    # Columnas para botones de acción
    col_down_md, col_down_pdf, col_log = st.columns([1, 1, 1.5])
    
    # 1. Botón Descargar Markdown
    with col_down_md:
        st.download_button(
            label="📥 Descargar Markdown",
            data=st.session_state.sa_generada,
            file_name="situacion_aprendizaje.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # 2. Botón Descargar PDF
    with col_down_pdf:
        pdf_bytes = crear_pdf(st.session_state.sa_generada)
        if pdf_bytes:
            st.download_button(
                label="📄 Descargar PDF",
                data=pdf_bytes,
                file_name="situacion_aprendizaje.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error("Error generando PDF")

    # 3. Botón REGISTRAR EN SHEETS (Objetivo 2)
    with col_log:
        if st.button("💾 Guardar en Registro (Google Sheets)", use_container_width=True, type="secondary"):
            with st.spinner("Conectando con la base de datos..."):
                # Intentamos identificar usuario
                user_email = "Anónimo/Local"
                try:
                    if st.context.headers.get("X-Shared-Secret"):
                         from streamlit.runtime.scriptrunner import get_script_run_ctx
                         ctx = get_script_run_ctx()
                         if ctx and hasattr(st, "experimental_user"):
                             user_email = st.experimental_user.email
                except:
                    pass

                # [CAMBIO IMPORTANTE] Recuperamos los datos del SNAPSHOT, no de los inputs vivos
                ctx = st.session_state.contexto_generacion
                
                # Preparamos los datos usando el contexto guardado
                # AHORA SE ENVÍAN LAS DOS COLUMNAS DE MODELOS
                datos_registro = [
                    str(datetime.now()),          # Timestamp
                    user_email,                   # Usuario
                    ctx.get("curso", ""),         # Curso (del snapshot)
                    ctx.get("ce", ""),            # CE (del snapshot)
                    ctx.get("cev", ""),           # CEv (del snapshot)
                    ctx.get("bloque", ""),        # Bloque (del snapshot)
                    ctx.get("sub", ""),           # Sub-apartado (del snapshot)
                    ctx.get("sb", ""),            # Saber Básico (del snapshot)
                    st.session_state.get('plan_json', 'No disponible'), # El plan JSON usado
                    st.session_state.sa_generada, # La SA FINAL (puede incluir ediciones manuales)
                    ctx.get("modelo_plan", "N/A"),# COLUMNA NUEVA: Modelo Plan
                    ctx.get("modelo_sa", "N/A"),  # COLUMNA NUEVA: Modelo SA
                    st.session_state.time_focus,  # Tiempo Foco
                    st.session_state.time_sa      # Tiempo SA
                ]
                
                exito = registrar_actividad(datos_registro)
                
                if exito:
                    st.success("✅ ¡Situación guardada correctamente en Google Sheets!")
                    st.balloons()
                else:
                    # El mensaje de error detallado ya se muestra dentro de registrar_actividad
                    pass

# ==============================================================================
# ZONA DE DEPURACIÓN (Objetivo 1)
# ==============================================================================
st.divider()

# Usamos un toggle para que sea más limpio que un expander fijo
if st.toggle("🛠️ Mostrar Memoria Interna (Debug Mode)"):
    st.info("Estas son las variables almacenadas actualmente en la sesión:")
    st.json(st.session_state)
    
    st.write("---")
    st.write("📂 **Variables de entorno (Selecciones actuales):**")
    st.write(f"**Curso:** {CURSO}")
    st.write(f"**CE:** {CE}")
    st.write(f"**TEMA:** {TEMA}")