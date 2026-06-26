import streamlit as st
import cv2
from ultralytics import YOLO
import time
import os
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LifeGuard AI - Live Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State for Log Persistence ---
if "logs" not in st.session_state:
    st.session_state.logs = [f"⏱ [SYSTEM LOG] Core pipeline hooked, ready. — {datetime.now().strftime('%H:%M:%S')}"]

# --- 2. DESIGN TOKENS ---
T = {
    "surface_container_lowest": "#0b0f10",
    "surface_container_low": "#191c1e",
    "surface_container": "#1d2022",
    "surface_container_high": "#272a2c",
    "on_surface": "#e0e3e5",
    "on_surface_variant": "#c6c6cd",
    "outline": "#909097",
    "outline_variant": "#45464d",
    "primary": "#bec6e0",
    "secondary": "#4edea3",           # Safe / Active / Normal
    "tertiary": "#7bd0ff",            # informational accents
    "error_container": "#93000a",
    "emergency_red": "#EF4444",       # high-alert states
    "on_background": "#e0e3e5",
}
SPACE = {"base": 4, "xs": 8, "sm": 16, "md": 24, "lg": 40, "xl": 64, "gutter": 20}
RADIUS = {"sm": 2, "default": 4, "md": 6, "lg": 8, "xl": 12, "full": 9999}

CANDIDATE_WEIGHTS = ["best.pt", "best-4.pt"]

@st.cache_resource
def load_yolo_model(candidates):
    for path in candidates:
        if os.path.exists(path):
            return YOLO(path), path
    return YOLO("yolov8n.pt"), "yolov8n.pt (fallback - no custom weights found)"

model, active_weights_path = load_yolo_model(CANDIDATE_WEIGHTS)

ALERT_KEYWORDS = ["fall", "fallen", "down", "lying", "faint", "collapse"]
model_class_names = model.names 

ALERT_CLASS_IDS = {
    idx for idx, name in model_class_names.items()
    if any(kw in str(name).lower() for kw in ALERT_KEYWORDS)
}
ALERT_ON_ANY_DETECTION = len(ALERT_CLASS_IDS) == 0

# --- 4. GLOBAL STYLE INJECTION ---
st.markdown(f"""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --surface-container-lowest: {T['surface_container_lowest']};
            --surface-container-low: {T['surface_container_low']};
            --surface-container: {T['surface_container']};
            --surface-container-high: {T['surface_container_high']};
            --on-surface: {T['on_surface']};
            --on-surface-variant: {T['on_surface_variant']};
            --outline: {T['outline']};
            --outline-variant: {T['outline_variant']};
            --primary: {T['primary']};
            --secondary: {T['secondary']};
            --tertiary: {T['tertiary']};
            --emergency-red: {T['emergency_red']};
            --sp-base: {SPACE['base']}px;
            --sp-xs: {SPACE['xs']}px;
            --sp-sm: {SPACE['sm']}px;
            --sp-md: {SPACE['md']}px;
            --radius-default: {RADIUS['default']}px;
            --radius-lg: {RADIUS['lg']}px;
            --radius-full: {RADIUS['full']}px;
        }}

        .stApp {{ background-color: var(--surface-container-lowest); color: var(--on-surface); font-family: 'Inter', sans-serif; }}
        div[data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{ padding-top: var(--sp-sm) !important; }}
        [data-testid="stSidebar"] {{ background-color: var(--surface-container-low); border-right: 1px solid var(--outline-variant); }}

        .mono {{ font-family: 'JetBrains Mono', monospace; }}
        .label-caps {{
            font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 500;
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--on-surface-variant);
        }}
        .data-mono {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; color: var(--secondary); }}

        .glass-panel {{
            background: var(--surface-container) !important;
            border: 1px solid var(--outline-variant) !important;
            padding: var(--sp-sm); border-radius: var(--radius-lg); position: relative;
        }}

        .accent-bar {{ position: absolute; top: 0; left: 0; bottom: 0; width: 2px; border-radius: var(--radius-default) 0 0 var(--radius-default); }}
        .accent-bar.ok {{ background: var(--secondary); }}
        .accent-bar.alert {{ background: var(--emergency-red); }}

        .live-feed-container {{
            position: relative; background: #000; border-radius: var(--radius-lg);
            overflow: hidden; border: 1px solid var(--outline-variant);
        }}
        .scanning-line {{
            position: absolute; top: 0; left: 0; width: 100%; height: 1px; background: var(--secondary);
            box-shadow: 0 0 12px rgba(78, 222, 163, 0.3); animation: scan 4s linear infinite;
            pointer-events: none; z-index: 10;
        }}
        @keyframes scan {{ 0% {{ top: 0; }} 100% {{ top: 100%; }} }}

        .ai-active-badge {{
            position: absolute; top: var(--sp-md); right: var(--sp-md); z-index: 11;
            background: var(--surface-container); border: 1px solid var(--outline-variant);
            border-radius: var(--radius-lg); padding: var(--sp-xs) var(--sp-sm);
            display: flex; align-items: center; gap: var(--sp-xs);
        }}
        .ai-active-badge.alert {{ border-color: var(--emergency-red); }}

        .pulse-dot {{
            width: 8px; height: 8px; border-radius: var(--radius-full); background: var(--secondary);
            display: inline-block; animation: pulse-glow 2s ease-out infinite;
        }}
        .pulse-dot.alert {{ background: var(--emergency-red); animation: pulse-glow-alert 1s ease-out infinite; }}
        @keyframes pulse-glow {{
            0% {{ box-shadow: 0 0 0 0 rgba(78, 222, 163, 0.45); }}
            70% {{ box-shadow: 0 0 0 8px rgba(78, 222, 163, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(78, 222, 163, 0); }}
        }}
        @keyframes pulse-glow-alert {{
            0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }}
            70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
        }}

        .status-pill {{
            background: rgba(78, 222, 163, 0.1); border: 1px solid rgba(78, 222, 163, 0.25); color: var(--secondary);
            padding: var(--sp-base) var(--sp-xs); border-radius: var(--radius-full);
            font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500; letter-spacing: 0.05em;
            display: inline-flex; align-items: center; gap: var(--sp-base);
        }}

        .zone-row {{
            display: flex; align-items: center; gap: var(--sp-sm); padding: var(--sp-xs) var(--sp-sm);
            border-radius: var(--radius-default); background: rgba(255,255,255,0.03);
            border: 1px solid var(--outline-variant); margin-bottom: var(--sp-xs);
        }}
        .zone-row.alert {{ border-color: var(--emergency-red); background: rgba(239, 68, 68, 0.08); }}

        .progress-track {{ width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: var(--radius-full); overflow: hidden; }}
        .progress-fill {{ height: 100%; border-radius: var(--radius-full); }}

        .stButton > button {{ border-radius: var(--radius-lg) !important; font-weight: 600 !important; border: 1px solid var(--
