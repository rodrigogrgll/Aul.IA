import streamlit as st
import google.generativeai as genai
import time
import markdown
from xhtml2pdf import pisa
import io
import streamlit.components.v1 as components
import pandas as pd
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Aul.IA - Diseño de Situaciones de Aprendizaje",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🎨 SISTEMA DE DISEÑO: MODERN SAAS UI v3.0 — INVESTOR READY (PREMIUM EDITION)
# ==============================================================================
st.markdown("""
<style>
    /* ========================================
       IMPORTS Y VARIABLES GLOBALES (REFINADAS)
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        /* Colores - Paleta más sofisticada y contrastada */
        --color-bg-primary: #FAFBFC;
        --color-bg-secondary: #FFFFFF;
        --color-bg-tertiary: #F3F4F6;
        --color-bg-elevated: #FFFFFF;
        
        /* Accent - Más saturado y premium */
        --color-accent-primary: #5046E5;
        --color-accent-primary-hover: #4338CA;
        --color-accent-primary-light: rgba(80, 70, 229, 0.08);
        --color-accent-primary-glow: rgba(80, 70, 229, 0.25);
        --color-accent-secondary: #06D6A0;
        --color-accent-secondary-light: rgba(6, 214, 160, 0.1);
        
        /* Texto - Mayor contraste */
        --color-text-primary: #111827;
        --color-text-secondary: #4B5563;
        --color-text-tertiary: #9CA3AF;
        --color-text-muted: #D1D5DB;
        
        /* Bordes más sutiles */
        --color-border: #E5E7EB;
        --color-border-light: #F3F4F6;
        --color-border-focus: var(--color-accent-primary);
        
        /* Sombras PREMIUM - Más suaves y difuminadas */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        --shadow-glow: 0 0 40px var(--color-accent-primary-glow);
        --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        
        /* Radios más modernos */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-full: 9999px;
        
        /* Transiciones suaves */
        --transition-fast: 120ms cubic-bezier(0.25, 0.1, 0.25, 1);
        --transition-base: 200ms cubic-bezier(0.25, 0.1, 0.25, 1);
        --transition-slow: 350ms cubic-bezier(0.25, 0.1, 0.25, 1);
        --transition-bounce: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    /* ========================================
       RESET Y LIMPIEZA DE STREAMLIT
       ======================================== */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* Header transparente pero funcional */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* Botón sidebar - ocultar texto "keyboard_double_arrow_right" */
    /* Selector amplio para capturar el botón en diferentes versiones de Streamlit */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="secondary"][data-testid="baseButton-secondary"],
    .stButton button,
    header button,
    [data-testid="stHeader"] button {
        font-size: 0 !important;
    }
    
    button[data-testid="collapsedControl"],
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        border-radius: 0 10px 10px 0 !important;
        min-width: 44px !important;
        height: 38px !important;
        padding: 0 12px !important;
        box-shadow: 2px 2px 12px rgba(79, 70, 229, 0.35) !important;
        border: none !important;
        font-size: 0 !important;
        color: transparent !important;
        overflow: hidden !important;
        position: relative !important;
    }
    
    button[data-testid="collapsedControl"] *,
    [data-testid="collapsedControl"] * {
        font-size: 0 !important;
        color: transparent !important;
        visibility: hidden !important;
    }
    
    button[data-testid="collapsedControl"]::after,
    [data-testid="collapsedControl"]::after {
        content: "☰ Menú" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: white !important;
        visibility: visible !important;
        white-space: nowrap !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    button[data-testid="collapsedControl"]:hover,
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
    }

    /* Quitar padding superior excesivo */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1120px !important;
    }
    
    /* ========================================
       FONDO - SUTIL Y PREMIUM (SIN PUNTOS)
       ======================================== */
    .stApp {
        background: linear-gradient(165deg, #FAFBFC 0%, #F0F4FF 35%, #FAFBFC 70%, #F5F3FF 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* SIN patrón de puntos - eliminado */
    .stApp::before {
        display: none !important;
    }

    /* ========================================
       SIDEBAR - EXPEDIENTE PREMIUM
       ======================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%) !important;
        border-right: 1px solid var(--color-border-light) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.75rem 1.25rem !important;
    }

    /* ========================================
       TIPOGRAFÍA GLOBAL (MÁS CONTRASTADA)
       ======================================== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--color-text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }
    
    h1 { font-size: 2.5rem !important; line-height: 1.15 !important; font-weight: 800 !important; }
    h2 { font-size: 1.875rem !important; line-height: 1.2 !important; }
    h3 { font-size: 1.375rem !important; line-height: 1.3 !important; font-weight: 600 !important; }
    
    p, span, label, div {
        font-family: 'Inter', sans-serif !important;
    }

    /* ========================================
       HEADER / BRAND - HERO SECTION
       ======================================== */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .brand-title {
        font-size: 2.75rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, var(--color-accent-primary) 0%, #7C3AED 50%, var(--color-accent-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.04em !important;
        position: relative;
    }
    
    .brand-subtitle {
        font-size: 1.05rem !important;
        color: var(--color-text-secondary) !important;
        font-weight: 400 !important;
        letter-spacing: -0.01em !important;
        max-width: 480px;
    }

    /* ========================================
       CARDS - ESTILO LINEAR/STRIPE
       ======================================== */
    .main-card {
        background: var(--color-bg-elevated);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 2.25rem 2.5rem;
        box-shadow: var(--shadow-card);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.4s ease-out;
    }
    
    /* Barra superior de acento - más refinada */
    .main-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
        opacity: 0.9;
    }
    
    /* Cards del expediente en sidebar - REDISEÑO */
    .expediente-card {
        background: var(--color-bg-elevated);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: 1rem 1.125rem;
        margin-bottom: 0.625rem;
        transition: all var(--transition-base);
    }
    
    .expediente-card:hover {
        border-color: var(--color-accent-primary);
        transform: translateX(2px);
    }
    
    .expediente-card-title {
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--color-text-muted);
        margin-bottom: 0.375rem;
    }
    
    .expediente-card-content {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--color-text-primary);
        line-height: 1.5;
    }
    
    /* Card completada - acento sutil sin border-left pesado */
    .expediente-card.completed {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.04) 0%, var(--color-bg-elevated) 100%);
        border-color: rgba(6, 214, 160, 0.3);
    }
    
    .expediente-card.completed .expediente-card-title {
        color: var(--color-accent-secondary);
    }
    
    /* Card pendiente */
    .expediente-card.pending {
        background: var(--color-bg-tertiary);
        border-style: dashed;
        border-color: var(--color-border);
        opacity: 0.7;
    }

    /* ========================================
       SIDEBAR BRAND - PREMIUM
       ======================================== */
    .sidebar-brand {
        text-align: center;
        padding: 1.25rem 0 1.75rem 0;
        border-bottom: 1px solid var(--color-border);
        margin-bottom: 1.5rem;
    }
    
    .sidebar-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--color-accent-primary-light), rgba(124, 58, 237, 0.08));
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.75rem auto;
        font-size: 1.5rem;
    }
    
    .sidebar-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    
    .sidebar-subtitle {
        font-size: 0.75rem;
        color: var(--color-text-tertiary);
        font-weight: 400;
    }
    
    /* Métricas del sidebar - REDISEÑO */
    .metric-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }
    
    .metric-card {
        flex: 1;
        background: var(--color-bg-tertiary);
        border-radius: var(--radius-md);
        padding: 0.875rem;
        text-align: center;
        border: 1px solid transparent;
        transition: all var(--transition-base);
    }
    
    .metric-card:hover {
        border-color: var(--color-border);
    }
    
    .metric-value {
        font-size: 1.625rem;
        font-weight: 800;
        color: var(--color-accent-primary);
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.6875rem;
        color: var(--color-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500;
    }

    /* ========================================
       BOTONES - ESTILO PREMIUM (VERCEL/LINEAR)
       ======================================== */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--color-accent-primary) 0%, #6366F1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        letter-spacing: -0.01em !important;
        transition: all var(--transition-base) !important;
        box-shadow: 0 4px 14px var(--color-accent-primary-glow), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        width: 100% !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] * {
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, var(--color-accent-primary-hover) 0%, #4F46E5 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px var(--color-accent-primary-glow), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
    }
    
    /* Botón secundario */
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background: var(--color-bg-elevated) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all var(--transition-base) !important;
        width: 100% !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
        background: var(--color-bg-tertiary) !important;
        border-color: var(--color-text-tertiary) !important;
    }

    /* Botón de éxito */
    .success-btn > button {
        background: linear-gradient(135deg, var(--color-accent-secondary) 0%, #059669 100%) !important;
        box-shadow: 0 4px 14px rgba(6, 214, 160, 0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        color: white !important;
    }
    
    .success-btn > button *,
    .success-btn > button span,
    .success-btn > button p {
        color: white !important;
    }
    
    .success-btn > button:hover {
        box-shadow: 0 8px 25px rgba(6, 214, 160, 0.45), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }

    /* ========================================
       INPUTS Y SELECTBOX - REFINADOS
       ======================================== */
    .stSelectbox > div > div {
        background: var(--color-bg-elevated) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        transition: all var(--transition-base) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--color-text-tertiary) !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--color-accent-primary) !important;
        box-shadow: 0 0 0 3px var(--color-accent-primary-light) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--color-bg-elevated) !important;
        border: 1.5px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.9375rem !important;
        transition: all var(--transition-base) !important;
    }
    
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: var(--color-text-tertiary) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--color-accent-primary) !important;
        box-shadow: 0 0 0 3px var(--color-accent-primary-light) !important;
        outline: none !important;
    }
    
    /* Labels - SIN EMOJIS, más limpios */
    .stSelectbox label, 
    .stTextInput label, 
    .stTextArea label {
        font-weight: 500 !important;
        color: var(--color-text-primary) !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.01em !important;
    }

    /* ========================================
       ALERTS / INFO BOXES - REFINADOS
       ======================================== */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border: none !important;
    }
    
    div[data-testid="stAlert"] {
        background: linear-gradient(135deg, var(--color-accent-primary-light) 0%, rgba(99, 102, 241, 0.06) 100%) !important;
        border-left: 3px solid var(--color-accent-primary) !important;
        padding: 1rem 1.25rem !important;
    }
    
    div[data-testid="stAlert"] p {
        color: var(--color-text-secondary) !important;
        font-size: 0.875rem !important;
    }

    /* ========================================
       DIVIDERS - MÁS SUTILES
       ======================================== */
    hr {
        border: none !important;
        height: 1px !important;
        background: var(--color-border) !important;
        margin: 1.75rem 0 !important;
        opacity: 0.6 !important;
    }

    /* ========================================
       DOWNLOAD BUTTONS
       ======================================== */
    .stDownloadButton > button {
        background: var(--color-bg-elevated) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all var(--transition-base) !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--color-accent-primary) !important;
        color: white !important;
        border-color: var(--color-accent-primary) !important;
    }

    /* ========================================
       TABS - ESTILO SEGMENT
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: var(--color-bg-tertiary);
        padding: 0.25rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        color: var(--color-text-secondary);
        font-size: 0.875rem;
        transition: all var(--transition-base);
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--color-bg-elevated) !important;
        color: var(--color-accent-primary) !important;
        box-shadow: var(--shadow-sm) !important;
        font-weight: 600 !important;
    }

    /* ========================================
       MARKDOWN TABLES - PREMIUM
       ======================================== */
    .stMarkdown table {
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        margin: 1.5rem 0 !important;
        font-size: 0.875rem !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        border: 1px solid var(--color-border) !important;
    }
    
    .stMarkdown th {
        background: var(--color-accent-primary) !important;
        color: white !important;
        padding: 1rem !important;
        text-align: left !important;
        font-weight: 600 !important;
        font-size: 0.8125rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    
    .stMarkdown td {
        padding: 0.875rem 1rem !important;
        border-bottom: 1px solid var(--color-border-light) !important;
        color: var(--color-text-secondary) !important;
    }
    
    .stMarkdown tr:last-child td {
        border-bottom: none !important;
    }
    
    .stMarkdown tr:nth-child(even) {
        background: var(--color-bg-tertiary) !important;
    }
    
    .stMarkdown tr:hover {
        background: var(--color-accent-primary-light) !important;
    }

    .stMarkdown h1 { margin-top: 0 !important; }
    .stMarkdown h3 { 
        color: var(--color-accent-primary) !important;
        margin-top: 1.5rem !important;
    }
    .stMarkdown ul { padding-left: 1.5rem !important; }
    .stMarkdown li { margin-bottom: 0.5rem !important; }

    /* ========================================
       LOADING CONTAINER
       ======================================== */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        background: var(--color-bg-elevated);
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
    }
    
    .loading-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
    }
    
    .loading-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text-primary);
        margin-bottom: 0.5rem;
    }
    
    .loading-subtitle {
        font-size: 0.9rem;
        color: var(--color-text-tertiary);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .animate-float { animation: float 3s ease-in-out infinite; }
    .animate-spin { animation: spin-slow 4s linear infinite; }

    /* ========================================
       ANIMACIONES GLOBALES
       ======================================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ========================================
       RESPONSIVE ADJUSTMENTS
       ======================================== */
    @media (max-width: 768px) {
        .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        .main-card {
            padding: 1.5rem 1.25rem;
        }
        
        .brand-title {
            font-size: 2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT PARA OCULTAR TEXTO DEL BOTÓN SIDEBAR ---
components.html("""
<script>
(function() {
    function fixSidebarButton() {
        // Buscar en el documento padre (donde está la UI de Streamlit)
        var doc = window.parent.document;
        
        // Buscar todos los elementos que contengan el texto del icono
        var walker = doc.createTreeWalker(
            doc.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        var nodesToHide = [];
        while(walker.nextNode()) {
            if(walker.currentNode.nodeValue.includes('keyboard_double_arrow_right') ||
               walker.currentNode.nodeValue.includes('keyboard_double_arrow_left')) {
                nodesToHide.push(walker.currentNode);
            }
        }
        
        nodesToHide.forEach(function(node) {
            var parent = node.parentElement;
            if(parent) {
                // Si es un botón, reemplazar su contenido
                if(parent.tagName === 'BUTTON' || parent.closest('button')) {
                    var btn = parent.tagName === 'BUTTON' ? parent : parent.closest('button');
                    btn.innerHTML = '<span style="font-size:14px;color:white;font-weight:600;">☰ Menú</span>';
                    btn.style.cssText = 'background:linear-gradient(135deg,#4F46E5,#6366F1)!important;border-radius:0 10px 10px 0!important;padding:8px 14px!important;border:none!important;box-shadow:2px 2px 12px rgba(79,70,229,0.35)!important;cursor:pointer!important;';
                } else {
                    // Ocultar el elemento padre
                    parent.style.display = 'none';
                }
            }
        });
        
        // También buscar por atributos data-testid
        var sidebarBtns = doc.querySelectorAll('[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"]');
        sidebarBtns.forEach(function(btn) {
            if(btn.textContent.includes('keyboard_double_arrow')) {
                btn.innerHTML = '<span style="font-size:14px;color:white;font-weight:600;">☰ Menú</span>';
                btn.style.cssText = 'background:linear-gradient(135deg,#4F46E5,#6366F1)!important;border-radius:0 10px 10px 0!important;padding:8px 14px!important;border:none!important;box-shadow:2px 2px 12px rgba(79,70,229,0.35)!important;cursor:pointer!important;display:flex!important;align-items:center!important;';
            }
        });
    }
    
    // Ejecutar múltiples veces para asegurar que capture el elemento
    fixSidebarButton();
    setTimeout(fixSidebarButton, 100);
    setTimeout(fixSidebarButton, 300);
    setTimeout(fixSidebarButton, 500);
    setTimeout(fixSidebarButton, 1000);
    setTimeout(fixSidebarButton, 2000);
    
    // Observar cambios en el DOM
    var observer = new MutationObserver(function(mutations) {
        fixSidebarButton();
    });
    
    var parentDoc = window.parent.document;
    if(parentDoc.body) {
        observer.observe(parentDoc.body, { childList: true, subtree: true, characterData: true });
    }
})();
</script>
""", height=0)

# --- JAVASCRIPT PARA SCROLL CINEMÁTICO ---
def scroll_to_top():
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        if (body) body.scrollTop = 0;
    </script>
    '''
    components.html(js, height=0)

# --- GESTIÓN DE ESTADO (WIZARD) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'input_curso' not in st.session_state: st.session_state.input_curso = "Selecciona un curso..."
if 'input_tema' not in st.session_state: st.session_state.input_tema = ""
if 'input_ce' not in st.session_state: st.session_state.input_ce = ""
if 'input_cev' not in st.session_state: st.session_state.input_cev = ""
if 'input_bloque' not in st.session_state: st.session_state.input_bloque = ""
if 'input_subapartado' not in st.session_state: st.session_state.input_subapartado = ""
if 'input_sb' not in st.session_state: st.session_state.input_sb = ""
if 'plan_de_foco' not in st.session_state: st.session_state.plan_de_foco = None
if 'plan_json' not in st.session_state: st.session_state.plan_json = None    
if 'sa_generada' not in st.session_state: st.session_state.sa_generada = None
if 'editor_sa' not in st.session_state: st.session_state.editor_sa = "Pulsa 'Crear Situación de Aprendizaje' para generar el contenido."

# --- API KEY ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo secrets.toml.")
except KeyError:
    st.error("⚠️ No se encontró la GOOGLE_API_KEY en secrets.toml.")

# --- MODELO ---
model = genai.GenerativeModel('models/gemini-2.0-flash')

# ==============================================================================
# LOGICA DE DATOS
# ==============================================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRp8yJQGCVyGEbrNn0zgEzy5-iLxhnS4fpA7oV6yA5bPA95wW6V0waRm78c6rea_A/pub?gid=650080582&single=true&output=csv" 
SHEET_SABERES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMvw6czNW_kcLWRp8WsxLfqc9FsYwb1Zi5rQmFMh7sQPRNUrH7yk0eNHXPxFQk8w/pub?gid=1639548304&single=true&output=csv" 

@st.cache_data 
def cargar_datos_csv(url):
    try:
        if "PON_AQUI" in url: return None 
        df = pd.read_csv(url, sep=",")
        if len(df.columns) <= 1:
            df = pd.read_csv(url, sep=";")
        df.columns = df.columns.str.strip()
        df = df.astype(str)
        return df
    except Exception as e:
        return None

df_curriculo = cargar_datos_csv(SHEET_URL)
df_saberes = cargar_datos_csv(SHEET_SABERES_URL) 

# --- FUNCIONES AUXILIARES ---
def crear_pdf(texto_markdown):
    html_content = markdown.markdown(texto_markdown, extensions=['tables'])
    estilos_css = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: Helvetica, sans-serif; font-size: 11pt; line-height: 1.6; color: #1a1a2e; }
        h1 { color: #5046E5; border-bottom: 3px solid #5046E5; padding-bottom: 8px; font-size: 22pt; }
        h2 { color: #6366F1; margin-top: 24px; font-size: 16pt; }
        h3 { color: #818CF8; font-size: 14pt; }
        p { margin-bottom: 12px; text-align: justify; }
        ul { margin-bottom: 12px; }
        li { margin-bottom: 6px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }
        th { background-color: #5046E5; color: white; border: 1px solid #5046E5; padding: 10px; text-align: left; font-weight: bold; }
        td { border: 1px solid #E5E7EB; padding: 10px; }
        tr:nth-child(even) { background-color: #F8FAFC; }
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
        placeholder.error(f"❌ Error al contactar con la IA: {e}")
        return None

# ==============================================================================
# 🎯 COMPONENTE: STEPPER DE PROGRESO (PREMIUM)
# ==============================================================================
def render_stepper(current_step):
    steps = [
        {"num": 1, "label": "Marco"},
        {"num": 2, "label": "Saberes"},
        {"num": 3, "label": "Estrategia"},
        {"num": 4, "label": "Resultado"}
    ]
    
    # Calcular progreso
    progress_pct = ((current_step - 1) / (len(steps) - 1)) * 100 if current_step > 1 else 0
    
    steps_html = ""
    for step in steps:
        if step["num"] < current_step:
            status = "completed"
            content = ""  # El checkmark se añade via CSS
        elif step["num"] == current_step:
            status = "active"
            content = str(step["num"])
        else:
            status = "pending"
            content = str(step["num"])
        
        steps_html += f'''
        <div class="step-item">
            <div class="step-circle {status}">{content}</div>
            <div class="step-label {status}">{step["label"]}</div>
        </div>
        '''
    
    stepper_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', -apple-system, sans-serif; 
                background: transparent;
                -webkit-font-smoothing: antialiased;
            }}
            
            .stepper-wrapper {{
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
                padding: 1.5rem 2.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
                position: relative;
            }}
            
            .stepper-container {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                position: relative;
            }}
            
            .stepper-line-bg {{
                position: absolute;
                top: 28px;
                left: 60px;
                right: 60px;
                height: 3px;
                background: #E5E7EB;
                border-radius: 999px;
                z-index: 1;
            }}
            
            .stepper-line-progress {{
                position: absolute;
                top: 28px;
                left: 60px;
                height: 3px;
                width: calc({progress_pct}% - {60 * progress_pct / 100}px);
                background: linear-gradient(90deg, #06D6A0, #5046E5);
                border-radius: 999px;
                z-index: 1;
                transition: width 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
            }}
            
            .step-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
                z-index: 2;
                flex: 1;
            }}
            
            .step-circle {{
                width: 56px;
                height: 56px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.25rem;
                margin-bottom: 0.75rem;
                transition: all 0.2s ease;
                background: white;
            }}
            
            .step-circle.completed {{
                background: #06D6A0;
                color: white;
                box-shadow: 0 0 0 4px rgba(6, 214, 160, 0.2), 0 4px 12px rgba(6, 214, 160, 0.25);
            }}
            
            .step-circle.completed::after {{
                content: "✓";
                font-size: 1.5rem;
            }}
            
            .step-circle.active {{
                background: linear-gradient(135deg, #5046E5, #6366F1);
                color: white;
                box-shadow: 0 0 0 4px rgba(80, 70, 229, 0.15), 0 8px 20px rgba(80, 70, 229, 0.3);
                animation: pulse 2.5s ease-in-out infinite;
            }}
            
            .step-circle.pending {{
                background: #F3F4F6;
                color: #D1D5DB;
                border: 2px solid #E5E7EB;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ 
                    box-shadow: 0 0 0 4px rgba(80, 70, 229, 0.15), 0 8px 20px rgba(80, 70, 229, 0.3);
                }}
                50% {{ 
                    box-shadow: 0 0 0 8px rgba(80, 70, 229, 0.08), 0 12px 30px rgba(80, 70, 229, 0.35);
                }}
            }}
            
            .step-label {{
                font-size: 0.875rem;
                font-weight: 600;
                text-align: center;
                letter-spacing: -0.01em;
            }}
            
            .step-label.completed {{ color: #06D6A0; }}
            .step-label.active {{ color: #5046E5; }}
            .step-label.pending {{ color: #D1D5DB; }}
        </style>
    </head>
    <body>
        <div class="stepper-wrapper">
            <div class="stepper-line-bg"></div>
            <div class="stepper-line-progress"></div>
            <div class="stepper-container">
                {steps_html}
            </div>
        </div>
    </body>
    </html>
    '''
    
    components.html(stepper_html, height=130)

# ==============================================================================
# 📁 COMPONENTE: SIDEBAR - EXPEDIENTE DEL PROYECTO (PREMIUM)
# ==============================================================================
def render_sidebar():
    with st.sidebar:
        # Header del sidebar - REDISEÑADO
        st.markdown('''
        <div class="sidebar-brand">
            <div class="sidebar-icon">📋</div>
            <div class="sidebar-title">Expediente del Proyecto</div>
            <div class="sidebar-subtitle">Registro de decisiones curriculares</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Métricas de progreso
        completed_steps = st.session_state.step - 1
        st.markdown(f'''
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">{st.session_state.step}</div>
                <div class="metric-label">Paso Actual</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{completed_steps}/4</div>
                <div class="metric-label">Completados</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SECCIÓN 1: MARCO PEDAGÓGICO
        st.markdown("#### Marco Pedagógico")
        
        if st.session_state.step >= 2 and st.session_state.input_curso != "Selecciona un curso...":
            # Curso
            st.markdown(f'''
            <div class="expediente-card completed">
                <div class="expediente-card-title">Curso</div>
                <div class="expediente-card-content">{st.session_state.input_curso}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Competencia Específica
            if st.session_state.input_ce:
                ce_truncated = st.session_state.input_ce[:120] + "..." if len(st.session_state.input_ce) > 120 else st.session_state.input_ce
                st.markdown(f'''
                <div class="expediente-card completed">
                    <div class="expediente-card-title">Competencia Específica</div>
                    <div class="expediente-card-content">{ce_truncated}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Criterio de Evaluación
            if st.session_state.input_cev:
                cev_truncated = st.session_state.input_cev[:120] + "..." if len(st.session_state.input_cev) > 120 else st.session_state.input_cev
                st.markdown(f'''
                <div class="expediente-card completed">
                    <div class="expediente-card-title">Criterio de Evaluación</div>
                    <div class="expediente-card-content">{cev_truncated}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="expediente-card pending">
                <div class="expediente-card-title">Pendiente</div>
                <div class="expediente-card-content">Completa el Paso 1</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SECCIÓN 2: SABERES Y CONTEXTO
        st.markdown("#### Saberes y Contexto")
        
        if st.session_state.step >= 3 and st.session_state.input_sb:
            # Bloque
            if st.session_state.input_bloque:
                st.markdown(f'''
                <div class="expediente-card completed">
                    <div class="expediente-card-title">Bloque</div>
                    <div class="expediente-card-content">{st.session_state.input_bloque}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Saber Básico
            sb_truncated = st.session_state.input_sb[:100] + "..." if len(st.session_state.input_sb) > 100 else st.session_state.input_sb
            st.markdown(f'''
            <div class="expediente-card completed">
                <div class="expediente-card-title">Saber Básico</div>
                <div class="expediente-card-content">{sb_truncated}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Tema
            if st.session_state.input_tema:
                st.markdown(f'''
                <div class="expediente-card completed">
                    <div class="expediente-card-title">Tema / Contexto</div>
                    <div class="expediente-card-content">{st.session_state.input_tema}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="expediente-card pending">
                <div class="expediente-card-title">Pendiente</div>
                <div class="expediente-card-content">Completa el Paso 2</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SECCIÓN 3: ESTRATEGIA
        st.markdown("#### Estrategia")
        
        if st.session_state.step >= 4 and st.session_state.plan_de_foco:
            st.markdown('''
            <div class="expediente-card completed">
                <div class="expediente-card-title">Plan de Foco</div>
                <div class="expediente-card-content">✅ Estrategia validada</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="expediente-card pending">
                <div class="expediente-card-title">Pendiente</div>
                <div class="expediente-card-content">Completa el Paso 3</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Footer del sidebar - MANTENIDO
        st.markdown("---")
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 0.75rem; color: var(--color-text-tertiary);">
                Powered by
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--color-accent-primary);">
                Aul.IA Engine v2.0
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ==============================================================================
# 🏠 HEADER PRINCIPAL (PREMIUM)
# ==============================================================================
def render_header():
    st.markdown('''
    <div class="brand-header">
        <span class="brand-title">Aul.IA</span>
    </div>
    <p class="brand-subtitle">Ingeniería curricular potenciada por IA</p>
    ''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 🚀 INTERFAZ DE USUARIO: FLUJO PASO A PASO (WIZARD)
# ==============================================================================

# Renderizar sidebar
render_sidebar()

# Renderizar header
render_header()

# Renderizar stepper
render_stepper(st.session_state.step)

# ------------------------------------------------------------------------------
# PASO 1: CONTEXTO Y COMPETENCIAS
# ------------------------------------------------------------------------------
if st.session_state.step == 1:
    
    # Card principal
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### Define el Marco Pedagógico")
    st.markdown("Establece las coordenadas curriculares de tu situación de aprendizaje.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_curriculo is not None:
        # CURSO
        cursos_disponibles = sorted(df_curriculo['Curso'].unique().tolist())
        idx_curso = 0
        if st.session_state.input_curso in cursos_disponibles:
            idx_curso = cursos_disponibles.index(st.session_state.input_curso) + 1

        sel_curso = st.selectbox(
            "Curso objetivo", 
            ["Selecciona un curso..."] + cursos_disponibles,
            index=idx_curso if st.session_state.input_curso != "Selecciona un curso..." else 0
        )
        st.session_state.input_curso = sel_curso

        if sel_curso != "Selecciona un curso...":
            df_curso_filtrado = df_curriculo[df_curriculo['Curso'] == sel_curso]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # CE
            opciones_ce_visual = df_curso_filtrado.apply(
                lambda x: f"{x['Codigo_CE']}: {x['Texto_CE']}", axis=1
            ).unique().tolist()
            
            sel_ce_completa = st.selectbox(
                "Competencia Específica (CE)", 
                ["Selecciona una competencia..."] + sorted(opciones_ce_visual)
            )
            
            if sel_ce_completa != "Selecciona una competencia...":
                codigo_ce_elegido = sel_ce_completa.split(":")[0].strip()
                st.session_state.input_ce = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]['Texto_CE'].iloc[0]
                
                st.markdown("<br>", unsafe_allow_html=True)

                # CEv
                df_ce_filtrado = df_curso_filtrado[df_curso_filtrado['Codigo_CE'] == codigo_ce_elegido]
                opciones_cev_visual = df_ce_filtrado.apply(
                    lambda x: f"{x['Codigo_CEv']}: {x['Texto_CEv']}", axis=1
                ).unique().tolist()
                
                sel_cev_completa = st.selectbox(
                    "Criterio de Evaluación (CEv)", 
                    ["Selecciona un criterio..."] + sorted(opciones_cev_visual)
                )
                
                if sel_cev_completa != "Selecciona un criterio...":
                    codigo_cev = sel_cev_completa.split(":")[0].strip()
                    st.session_state.input_cev = df_ce_filtrado[df_ce_filtrado['Codigo_CEv'] == codigo_cev]['Texto_CEv'].iloc[0]
            else:
                st.session_state.input_ce = ""
                st.session_state.input_cev = ""
        else:
            st.info("Selecciona un curso para ver las competencias disponibles.")
    else:
        st.error("❌ No se pudieron cargar los datos curriculares. Modo manual activado.")
        st.session_state.input_curso = st.selectbox("Curso", ["5º Primaria", "6º Primaria"])
        st.session_state.input_ce = st.text_area("Competencia Específica", value=st.session_state.input_ce)
        st.session_state.input_cev = st.text_area("Criterio de Evaluación", value=st.session_state.input_cev)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón de continuar
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continuar →", type="primary", use_container_width=True):
            if (st.session_state.input_ce and 
                st.session_state.input_cev and
                st.session_state.input_curso != "Selecciona un curso..."):
                st.session_state.step = 2
                scroll_to_top()
                st.rerun()
            else:
                st.warning("Por favor, completa todos los campos para continuar.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PASO 2: SABERES BÁSICOS
# ------------------------------------------------------------------------------
elif st.session_state.step == 2:
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### Contenidos y Contexto")
    st.markdown(f"Define los saberes básicos y el contexto temático para **{st.session_state.input_curso}**.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_saberes is not None:
        # BLOQUE
        bloques_disponibles = sorted(df_saberes['Bloque'].unique().tolist())
        idx_bloque = 0
        if st.session_state.input_bloque in bloques_disponibles:
            idx_bloque = bloques_disponibles.index(st.session_state.input_bloque) + 1

        sel_bloque = st.selectbox(
            "Bloque de contenidos", 
            ["Selecciona un bloque..."] + bloques_disponibles, 
            index=idx_bloque
        )
        
        if sel_bloque != "Selecciona un bloque...":
            st.session_state.input_bloque = sel_bloque
            df_bloque_filtrado = df_saberes[df_saberes['Bloque'] == sel_bloque]
            
            st.markdown("<br>", unsafe_allow_html=True)

            # SUB-APARTADO
            sub_disponibles = sorted(df_bloque_filtrado['Sub-apartado'].unique().tolist())
            idx_sub = 0
            if st.session_state.input_subapartado in sub_disponibles:
                idx_sub = sub_disponibles.index(st.session_state.input_subapartado) + 1
            
            sel_sub = st.selectbox(
                "Sub-apartado", 
                ["Selecciona un sub-apartado..."] + sub_disponibles, 
                index=idx_sub
            )

            if sel_sub != "Selecciona un sub-apartado...":
                st.session_state.input_subapartado = sel_sub
                df_sub_filtrado = df_bloque_filtrado[df_bloque_filtrado['Sub-apartado'] == sel_sub]
                
                st.markdown("<br>", unsafe_allow_html=True)

                # SABERES
                col_saberes_name = 'Saberes Básicos (Contenidos Concretos)'
                if col_saberes_name not in df_saberes.columns:
                    col_candidates = [c for c in df_saberes.columns if c.startswith('Saberes')]
                    if col_candidates: col_saberes_name = col_candidates[0]

                saberes_disponibles = df_sub_filtrado[col_saberes_name].unique().tolist()
                idx_sb = 0
                if st.session_state.input_sb in saberes_disponibles:
                    idx_sb = saberes_disponibles.index(st.session_state.input_sb) + 1
                
                sel_sb = st.selectbox(
                    "Saberes Básicos (SB)", 
                    ["Selecciona un saber..."] + saberes_disponibles, 
                    index=idx_sb
                )
                
                if sel_sb != "Selecciona un saber...":
                    st.session_state.input_sb = sel_sb
        
        if st.session_state.input_sb:
            st.success(f"✅ Seleccionado: {st.session_state.input_sb}")
    else:
        st.error("❌ No se pudieron cargar los datos de Saberes. Modo manual activado.")
        st.session_state.input_bloque = st.text_input("Bloque:", value=st.session_state.input_bloque)
        st.session_state.input_subapartado = st.text_input("Sub-apartado:", value=st.session_state.input_subapartado)
        st.session_state.input_sb = st.text_area("Saberes Básicos (SB):", value=st.session_state.input_sb)
    
    st.markdown("---")
    
    # TEMA / CONTEXTO
    st.markdown("#### Tema o Hilo Conductor")
    st.info("Es recomendable que el tema esté relacionado tanto con la Competencia Específica como con el Saber Básico.")
    
    st.session_state.input_tema = st.text_input(
        "Tema, Hilo Conductor o Contexto:",
        value=st.session_state.input_tema,
        placeholder="Ej: El ciclo del agua en nuestra comunidad...",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botones de navegación
    col_back, col_spacer, col_next = st.columns([1, 1, 1])
    with col_back:
        if st.button("← Atrás", use_container_width=True):
            st.session_state.step = 1
            scroll_to_top()
            st.rerun()
    with col_next:
        if st.button("Generar Estrategia →", type="primary", use_container_width=True):
            if (st.session_state.input_sb and 
                st.session_state.input_sb != "Selecciona un saber..." and 
                st.session_state.input_tema):
                st.session_state.step = 3
                scroll_to_top()
                st.rerun()
            else:
                st.warning("Por favor, selecciona los Saberes Básicos y escribe un Tema.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PASO 3: PLAN DE FOCO
# ------------------------------------------------------------------------------
elif st.session_state.step == 3:
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### Brújula Estratégica")
    st.markdown("La IA analiza tu marco pedagógico y propone un enfoque estratégico optimizado.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    CURSO = st.session_state.input_curso
    TEMA = st.session_state.input_tema
    CE = st.session_state.input_ce
    CEv = st.session_state.input_cev
    SB = st.session_state.input_sb
    
    contenedor_plan = st.empty()
    
    if not st.session_state.plan_de_foco:
        contenedor_plan.markdown('''
        <div class="loading-container">
            <div class="loading-icon animate-spin">🧭</div>
            <div class="loading-title">Calibrando Brújula Pedagógica...</div>
            <div class="loading-subtitle">Analizando el marco curricular y generando estrategia</div>
        </div>
        ''', unsafe_allow_html=True)
        
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
                Paso 4 (Renuncia Estratégica): Declara qué elementos del análisis inicial quedan fuera del foco y justifícalo brevemente.
                Paso 5 (Esencia Competencial - EsCE): Genera una frase síntesis que fusione el foco realista del Eje (QUÉ) y de las Herramientas (CÓMO). Este es el INPUT NUCLEAR que se usará para el siguiente proceso. Formato obligatorio: [Infinitivo] + [Gerundio] + [Finalidad]. Ejemplo: "Representar información estadística construyendo gráficos de barras para comunicar datos de forma clara".
                
                SALIDA ESPERADA (En dos bloques):
                ## 📊 Plan de Foco Estratégico
                (Contenido legible para el profesor, incluyendo los 5 pasos)
                
                ___SEPARADOR___
                
                (El JSON con la Esencia Competencial y datos estructurados)
                {{
                "planDeFoco": {{
                    "paso1_analisis": {{
                    "ejeCompetencial_QUE": "...",
                    "herramientasAnalisis_COMO": "..."
                    }},
                    "paso2_adecuacion": {{
                    "conceptosDirectos": "...",
                    "conceptosAdaptar": "..."
                    }},
                    "paso3_focoRealista": {{
                    "focoEje_QUE": "Declaración del foco en el Eje y su finalidad...",
                    "focoHerramientas_COMO": "Declaración del foco en las Herramientas..."
                    }},
                    "paso4_renunciaEstrategica": "Declaración y justificación de los elementos fuera de foco..."
                }},
                "esenciaCompetencial_EsCE": "Párrafo único con la síntesis en formato: Infinitivo + Gerundio + Finalidad."
                }}
        """
        
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

    if st.session_state.plan_de_foco:
        contenedor_plan.markdown(st.session_state.plan_de_foco)
        
        st.markdown("---")
        
        col_ok, col_spacer, col_ko = st.columns([2, 1, 1])
        with col_ok:
            st.markdown('<div class="success-btn">', unsafe_allow_html=True)
            if st.button("Estrategia Correcta: Crear SA →", type="primary", use_container_width=True):
                st.session_state.step = 4
                scroll_to_top()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_ko:
            if st.button("Reiniciar", use_container_width=True):
                st.session_state.plan_de_foco = None
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PASO 4: GENERACIÓN FINAL
# ------------------------------------------------------------------------------
elif st.session_state.step == 4:
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### Situación de Aprendizaje")
    st.markdown("Generación completa de la situación de aprendizaje con rúbrica de evaluación.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    contenedor_final = st.empty()
    
    CURSO = st.session_state.input_curso
    TEMA = st.session_state.input_tema
    CEv = st.session_state.input_cev
    SB = st.session_state.input_sb
    
    if not st.session_state.sa_generada:
        json_recuperado = st.session_state.plan_json
        
        EsCE = "Competencia Específica definida en el plan estratégico."
        try:
            datos_plan = json.loads(json_recuperado)
            if "esenciaCompetencial_EsCE" in datos_plan:
                EsCE = datos_plan["esenciaCompetencial_EsCE"]
        except Exception as e:
            pass

        contenedor_final.markdown('''
        <div class="loading-container">
            <div class="loading-icon animate-float">🧠</div>
            <div class="loading-title">El Artesano Digital está pensando...</div>
            <div class="loading-subtitle">Conectando saberes, diseñando contexto y estructurando rúbrica</div>
        </div>
        ''', unsafe_allow_html=True)
        
        PROMPT_FABRICACION = f"""
                Rol: Actúa como un Ingeniero Curricular LOMLOE experto en diseño técnico de Situaciones de Aprendizaje. Tu prioridad es la precisión estructural y la coherencia evaluativa, por encima de la creatividad literaria.
                
                Contexto: Te proporcionaré variables de entrada definidas por el usuario y un plan estratégico JSON.
                
                VARIABLES DEL USUARIO:
                - Criterio de Evaluación: {CEv}. El estándar de referencia oficial. Define la profundidad y complejidad esperada en el desempeño.
                - Saberes Básicos: {SB}. Son los conocimientos necesarios para lograr el desarrollo de las competencias. No son adornos; son herramientas. Debes verificar si las tareas obligan a usarlos.
                - Tema/Contenido: {TEMA}. El contexto semántico
                - Curso: {CURSO}. El nivel madurativo. Se usa como criterio para ajustar la complejidad.
                - PLAN ESTRATÉGICO (JSON): {json_recuperado}. Dentro de este json SOLO tienes que utilizar la {EsCE}. Es el input nuclear derivado del Planificador. Actúa como el proxy de la Competencia Específica (CE), la cual no define intenciones abstractas, sino actuaciones concretas formadas por la tríada: una acción, unos saberes a movilizar y un contexto de ejecución.
                
                Instrucción de Tarea (Crítica): Tu trabajo es generar el contenido pedagógico de la Situación de Aprendizaje. Tu respuesta debe contener ÚNICAMENTE las secciones 1, 2, 3,  4 y 5.
                
                Tarea: Genera la Situación de Aprendizaje siguiendo estas instrucciones paso a paso:

                1. Título de la Situación de Aprendizaje
                (Genera un título atractivo que combine el {TEMA} y el desafío).

                2. Enfoque Curricular 
                - Saberes Básicos Movilizados: (Confirma y lista los {SB} proporcionados).
                - Conexiones Curriculares: (Menciona brevemente si la SA trabaja de forma secundaria otras competencias o materias).

                3. Objetivos Competenciales (OC) e Indicadores de Logro (IL)
                Esta sección construye la arquitectura evaluativa. Debes generar 2 Binomios (Pares Indisolubles) siguiendo una estricta lógica de derivación.
                
                INSTRUCCIONES DE GENERACIÓN:
                
                PASO 1: Define el Objetivo Competencial (OC) - "La Intención Situada"
                Función: Es una relectura de la Competencia Específica ({EsCE}) para esta SA.
                Acción: Fusiona la {EsCE} con los {SB} y el {TEMA}.
                ESTRUCTURA TRIÁDICA OBLIGATORIA: Debes construir la frase con estos 3 elementos:
                Acción (Verbo): La operación cognitiva o motriz.
                Objeto (Saber): El {SB} o contenido que se manipula.
                Contexto/Finalidad: Para qué o dónde se aplica.
                REGLA DE VALIDACIÓN DEL VERBO (Lógica Condicional): Aplica este algoritmo para validar el verbo inicial:
                CASO A: Verbos de Producción Tangible (Diseñar, Construir, Elaborar, Escribir).
                Estado: VÁLIDOS por sí mismos. Implican un producto.
                CASO B: Verbos Mentales/Cognitivos (Analizar, Valorar, Argumentar, Interpretar, Justificar).
                Estado: VÁLIDOS SOLO SI especificas inmediatamente el CANAL, FORMATO o MEDIO.
                Ejemplo INCORRECTO: "Argumentar las consecuencias del cambio climático..." (¿Dónde? ¿En su cabeza?).
                Ejemplo CORRECTO: "Argumentar en un debate oral las consecuencias..." o "Valorar en un informe técnico las consecuencias...".
                Regla de Viabilidad Material ({CURSO}): Los OC deben estar ajustados a la madurez cognitiva del {CURSO}
                
                PASO 2: Define el Indicador de Logro (IL) - "La Evidencia Tangible"
                Función: Precisar la actuación observable que valida el OC.
                ⚠️ GUARDARRAÍL DE VALIDACIÓN (CRÍTICO): Para dar por válido un IL, este debe cumplir simultáneamente dos condiciones:
                Ser una relectura contextualizada del Criterio de Evaluación ({CEv}).
                Describir una actuación observable derivada directamente del OC formulado.
                Si el IL no cumple ambas (conexión legal + conexión con la tarea), es inválido.
                Regla de Viabilidad Material ({CURSO}): La evidencia o producto exigido debe ser realizable por la madurez motriz y cognitiva del {CURSO}
                SALIDA REQUERIDA (Genera 2 Binomios):
                BINOMIO 1 (Foco en el Proceso/Indagación):
                OC 1: (Relectura de la {EsCE} centrada en la construcción del saber).
                IL 1: (Evidencia intermedia derivada del OC 1 y del CEv. Ej: Registros, mapas).
                BINOMIO 2 (Foco en el Producto/Transferencia):
                OC 2: (Relectura de la {EsCE} centrada en la resolución del reto).
                IL 2: (Evidencia final derivada del OC 2 y del CEv. Ej: Producto Final o Actuación compleja).
                
            4. Situación de Aprendizaje (SA) - EL GUION NARRATIVO 
                
                Esta sección no es una lista de actividades, es el guion de una misión. Tu objetivo es diseñar un flujo donde la narrativa y la pedagogía sean indivisibles.
                A) Escenario y Rol Colectivo (El Marco de Ficción) NO describas un tema genérico. Define un ESCENARIO ESPECÍFICO y otorga al alumnado un ROL COLECTIVO ACTIVO que mejor se ajuste a la naturaleza del {TEMA} y del {CURSO}.
                Restricción de Persistencia: Este ROL es INMUTABLE. Debe mantenerse activo desde la primera hasta la última tarea. Prohibido cambiar de rol a mitad de la SA (ej. no pueden ser científicos en la tarea 1 y periodistas en la 3).
                El Reto: Plantea el conflicto que este ROL debe resolver, conectando con una necesidad real o verosímil.
                B) Producto Final Define la meta tangible (Debe coincidir con el IL 2). Asegúrate de que el producto sea coherente con el ROL (ej. Si son arquitectos, entregan planos/maquetas, no un mural escolar).
                C) Secuencia de Actuación (Hilo Conductor) Diseña una secuencia lógica. REGLA DE COHERENCIA ARTEFACTUAL (CRÍTICA): Antes de describir las tareas, mira los IL 1 e IL 2. La actividad debe ser el proceso exacto de fabricación de esas evidencias. REGLA DE CADENA CAUSAL: Evita la "lista de la compra". La Tarea N debe generar un insumo o conocimiento necesario para resolver la Tarea N+1.
                
                Genera los siguientes 5 MOMENTOS PEDAGÓGICOS integrados en la historia:
                
                1. Momento de Anclaje (La Misión):
                El ROL recibe el encargo, detecta el problema o se encuentra con el conflicto. Tareas de activación y conexión con los conocimientos previos y motivación situadas.
                
                2. Momento de Construcción Técnica (La Llave Maestra - Movilización de Saberes):
                Función: El ROL necesita adquirir/usar el Saber Básico {SB} como herramienta indispensable para avanzar.
                Requisito de Bloqueo (Evaluador 2A): Diseña la tarea de modo que sea IMPOSIBLE de resolver con éxito usando solo sentido común. El alumno debe verse obligado a manipular el concepto técnico del {SB}.
                Instrucción de Redacción: "Los [Nombre del Rol] [Acción] utilizando [Saber Básico] para [Finalidad del reto]".
                Coherencia: Aquí se genera la evidencia del IL 1.  Describe paso a paso cómo los alumnos construyen la evidencia material definida en el IL 1
                Secuencia lógica: "Los [Rol] se enfrentan al problema [X]. Para resolverlo, deben aplicar [Saber Básico] mediante la técnica de [Actividad concreta], obteniendo como resultado [Evidencia para IL 1]."

                3. Momento de Acción Social (Mecánica de Interdependencia):
                Requisito (Evaluador 2B): No digas solo "en grupos". Define la Mecánica de Colaboración necesaria para el ROL. ¿Por qué necesitan a los demás? (Ej. Reparto de información tipo puzle, consenso necesario, roles de gestión interna, revisión de pares).  Integra dinámicas de trabajo cooperativo donde el éxito dependa de la interacción (no solo trabajo en paralelo).

                4. Momento de Transferencia:
                Creación: El ROL aplica lo aprendido para materializar el Producto Final (IL 2). Describe cómo se materializa el producto final.
                Andamiaje Decreciente: Describe cómo el docente pasa de guiar a facilitar, otorgando decisiones de diseño al alumno. Describe una situación donde el docente presenta el OBJETIVO y los CRITERIOS DE CALIDAD, pero los alumnos deciden la ESTRATEGIA o el FORMATO.
                
                5. Momento de Metacognición (Cierre):
                Cambio de Foco (Del Medio al Fin): La reflexión NO debe centrarse únicamente en si usaron bien el Saber Básico (eso es técnico). Debe centrarse en si alcanzaron los Objetivos Competenciales (OCs) de la misión.
                La Dinámica: Diseña una "Reunión de Lecciones Aprendidas" dentro del ROL.
                Las 3 Dimensiones Obligatorias del Debriefing:
                Auditoría de Objetivos (El QUÉ): ¿Cumplimos la misión? Conecta el resultado final con el OC. (Ej. "Como arquitectos, ¿es nuestro puente seguro y eficiente? ¿Hemos logrado el objetivo de sostenibilidad?").
                Análisis de Estrategia (El CÓMO): ¿Qué obstáculos mentales encontramos y cómo los superamos? Reflexión sobre la gestión del error y la autorregulación. (Ej. "¿Dónde nos atascamos? ¿Fue útil dividirnos las tareas o deberíamos haber trabajado juntos todo el tiempo?").
                Proyección de Transferencia (El PARA QUÉ): ¿En qué otras "misiones" futuras (de la vida real o de la asignatura) podríamos usar estas mismas estrategias?
                Prohibición: Evita preguntas de satisfacción emocional simple ("¿Os ha gustado?"). Busca la toma de conciencia del aprendizaje.

            5. Rúbrica de Evaluación

                Debes generar una tabla de evaluación técnica. No improvises los descriptores. Construye cada celda aplicando estrictamente las siguientes Reglas de Ingeniería Evaluativa:
                
                A) INPUTS (Filas de la Tabla):
                Usa los 2 Binomios (OC + IL) definidos en la Sección 3.
            
                B) REGLA DE FUSIÓN SEMÁNTICA (Anti-Abstracción)
                Todo descriptor debe mencionar: Acción Cognitiva (OC) + Evidencia Material (IL).
                Mal: "Analiza muy bien".
                Bien: "Analiza las causas en el informe final...".
                
                C) REGLA DE PROGRESIÓN (Madurez Cognitiva):
                Diferencia los niveles combinando estas 4 variables de madurez, no contando errores:
                Autonomía: Grado de dependencia del docente.
                Complejidad: Capacidad de manejar variables (una variable vs. múltiples variables).
                Justificación: Capacidad de aportar evidencias o razones (opinión vs. argumento).
                Estabilidad: Consistencia del desempeño (errático vs. sistemático).
                
                D) MATRIZ DE REDACCIÓN DE NIVELES (Lógica de Progresión): N. Aplica estas 4 definiciones lógicas para redactar el texto de cada nivel:
                NIVEL 1 (EN INICIO) -> Criterio: Inestabilidad y Dependencia.
                Instrucción: Redacta describiendo un desempeño fragmentario. El alumno intenta la acción pero presenta errores conceptuales, omisiones graves o necesita guía constante del docente para avanzar.
                NIVEL 2 (EN DESARROLLO) -> Criterio: Estabilidad Básica.
                Instrucción: Redacta describiendo un desempeño correcto solo en lo simple. El alumno resuelve los aspectos básicos de la tarea, pero su respuesta es superficial, carece de matices o falla al enfrentar la complejidad.
                NIVEL 3 (COMPETENTE) -> Criterio: Suficiencia Técnica (El Estándar).
                Instrucción: Redacta describiendo un desempeño autónomo y correcto. El alumno cumple todos los requisitos técnicos del Criterio de Evaluación sin errores relevantes y con justificación válida.
                NIVEL 4 (EXPERTO) -> Criterio: Excelencia y Transferencia.
                Instrucción: Redacta describiendo un desempeño profundo y sistemático. El alumno no solo cumple, sino que aporta justificaciones complejas, demuestra un hábito consolidado (estabilidad total) o es capaz de transferir el saber a situaciones nuevas/distintas.
                
                Formato de Salida (Tabla Markdown): | Objetivo Competencial (OC) + Indicador (IL) | Nivel 1 (Inicio) | Nivel 2 (Desarrollo) | Nivel 3 (Competente) | Nivel 4 (Experto) | | :--- | :--- | :--- | :--- | :--- | | OC 1: [Texto OC]IL 1: [Texto IL] | [Descriptor N1] | [Descriptor N2] | [Descriptor N3] | [Descriptor N4] | | OC 2: [Texto OC] IL 2: [Texto IL] | [Descriptor N1] | [Descriptor N2] | [Descriptor N3] | [Descriptor N4] |
                        
        """
        
        resultado_sa = stream_gemini_response(PROMPT_FABRICACION, contenedor_final)
        
        if resultado_sa:
            st.session_state.sa_generada = resultado_sa
            st.session_state.editor_sa = resultado_sa
            st.rerun()

    # VISUALIZACIÓN DE RESULTADOS
    if st.session_state.sa_generada:
        with contenedor_final.container():
            tab_vista, tab_editor = st.tabs(["Vista Previa", "Editor"])

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

        st.markdown("---")
        
        # Botones de descarga y reinicio
        st.markdown("#### Exportar tu Situación de Aprendizaje")
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.download_button(
                label="Descargar MD",
                data=st.session_state.sa_generada,
                file_name="situacion_aprendizaje.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
            pdf_bytes = crear_pdf(st.session_state.sa_generada)
            if pdf_bytes:
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_bytes,
                    file_name="situacion_aprendizaje.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with col4:
            if st.button("Nueva SA", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)