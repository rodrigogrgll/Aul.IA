import streamlit as st
import google.generativeai as genai
import time 
import markdown # [NUEVO] Para convertir Markdown a HTML
from xhtml2pdf import pisa # [NUEVO] Para convertir HTML a PDF
import io # [NUEVO] Para manejar el archivo en memoria

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide") 

# Cargar la API Key
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except FileNotFoundError:
    st.error("No se encontró el archivo secrets.toml.")
except KeyError:
    st.error("No se encontró la GOOGLE_API_KEY en secrets.toml.")

# --- CONFIGURACIÓN DEL MODELO ---
model = genai.GenerativeModel('models/gemini-2.5-pro') 

# [NUEVO] Función para generar el PDF
def crear_pdf(texto_markdown):
    # 1. Convertir Markdown a HTML (incluyendo extensión de tablas)
    html_content = markdown.markdown(texto_markdown, extensions=['tables'])
    
    # 2. Añadir estilos CSS para que el PDF se vea profesional
    estilos_css = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: Helvetica, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
        h1 { color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 5px; }
        h2 { color: #283593; margin-top: 20px; }
        h3 { color: #303f9f; }
        p { margin-bottom: 10px; text-align: justify; }
        ul { margin-bottom: 10px; }
        /* Estilos para las tablas */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }
        th { background-color: #e8eaf6; color: #1a237e; border: 1px solid #ccc; padding: 8px; text-align: left; }
        td { border: 1px solid #ccc; padding: 8px; }
    </style>
    """
    
    html_completo = f"<html><head>{estilos_css}</head><body>{html_content}</body></html>"
    
    # 3. Convertir HTML a PDF usando xhtml2pdf
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_completo, dest=pdf_buffer)
    
    if pisa_status.err:
        return None
    
    return pdf_buffer.getvalue()

def llamar_a_gemini(prompt_usuario):
    try:
        response = model.generate_content(prompt_usuario)
        return response.text
    except Exception as e:
        st.error(f"Error al contactar con la IA: {e}")
        return None

# Función streaming (Con lógica para ocultar JSON y evitar errores)
def stream_gemini_response(prompt_usuario, placeholder):
    full_text = ""
    stop_updating_ui = False 

    try:
        response = model.generate_content(prompt_usuario, stream=True)
        for chunk in response:
            try:
                if chunk.text:
                    full_text += chunk.text
                    
                    # Ocultar JSON si aparece el separador
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
        placeholder.error(f"Error al contactar con la IA: {e}")
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

# --- TÍTULO Y PANELES ---
st.title("Aul.IA: Creación de Situaciones de Aprendizaje")
col1, col2 = st.columns([1, 2])

# --- PANEL DERECHO (INPUTS) ---
with col2:
    st.subheader("Paso 1: Define tus 5 variables")
    CURSO = st.selectbox("Elige el curso:", ("5º Primaria", "6º Primaria"))
    TEMA = st.text_input("Contenido concreto o pretexto:")
    CE = st.text_area("Competencia Específica (CE):", height=100)
    CEv = st.text_area("Criterio de Evaluación (CEv):", height=100)
    SB = st.text_area("Saberes Básicos (SB):", height=100)

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

# --- BOTÓN 1: Generar Plan ---
with col_btn1:
    if st.button("Generar Plan de Foco Estratégico", use_container_width=True):
        if not CE or not CEv or not TEMA or not SB or not CURSO:
            st.error("Por favor, rellena todos los campos antes de generar el Plan de Foco.")
        else:
            # ==============================================================================
            #  🔵  ANIMACIÓN: BRÚJULA ESTRATÉGICA  🔵
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
            
            respuesta_ia = stream_gemini_response(prompt_temporal_plan_foco, contenedor_plan)

            if respuesta_ia:
                if "___SEPARADOR___" in respuesta_ia:
                    partes = respuesta_ia.split("___SEPARADOR___")
                    st.session_state.plan_de_foco = partes[0].strip()
                    st.session_state.plan_json = partes[1].strip()
                    st.rerun()
                else:
                    st.warning("La IA no generó el separador. Mostrando respuesta completa.")
                    st.session_state.plan_de_foco = respuesta_ia
                    st.session_state.plan_json = respuesta_ia 

# --- BOTÓN 2: Solo dibujamos el botón (La lógica va abajo) ---
with col_btn2:
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
        
        # [STREAMING] Escribimos directamente en el contenedor del paso 4
        resultado_sa = stream_gemini_response(PROMPT_FABRICACION, contenedor_paso_4)

        if resultado_sa:
            st.session_state.sa_generada = resultado_sa
            st.session_state.editor_sa = resultado_sa 
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
                height=600, 
                key="editor_sa",
                label_visibility="collapsed" 
            )
            if sa_final_editada != st.session_state.sa_generada:
                st.session_state.sa_generada = sa_final_editada

else:
    if not btn_crear_sa:
        contenedor_paso_4.info("Pulsa 'Crear Situación de Aprendizaje' arriba para generar el contenido.")

# ZONA DE DESCARGA
mensaje_inicial = "Pulsa 'Crear Situación de Aprendizaje' arriba para generar el contenido."

if st.session_state.sa_generada and st.session_state.sa_generada != mensaje_inicial:
    st.markdown("---")
    # [NUEVO] Layout de columnas para los dos botones
    col_down_md, col_down_pdf, col_void = st.columns([1, 1, 2])
    
    with col_down_md:
        st.download_button(
            label="📥 Descargar Markdown",
            data=st.session_state.sa_generada,
            file_name="situacion_aprendizaje.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col_down_pdf:
        # Generar PDF en vuelo
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
            st.error("Error al generar PDF")

# --- ZONA DE DEPURACIÓN ---
st.divider()
with st.expander("🔍 MODO DESARROLLADOR: Ver Memoria Interna"):
    st.write(st.session_state)