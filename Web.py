import streamlit as st
import cv2
from ultralytics import YOLO
import os
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration, WebRtcMode

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
    "secondary": "#4edea3",           
    "tertiary": "#7bd0ff",            
    "error_container": "#93000a",
    "emergency_red": "#EF4444",       
    "on_background": "#e0e3e5",
}
SPACE = {"base": 4, "xs": 8, "sm": 16, "md": 24, "lg": 40, "xl": 64, "gutter": 20}
RADIUS = {"sm": 2, "default": 4, "md": 6, "lg": 8, "xl": 12, "full": 9999}

CANDIDATE_WEIGHTS = ["best-5.pt", "best-5.pt"]

@st.cache_resource
def load_yolo_model(candidates):
    for path in candidates:
        if os.path.exists(path):
            return YOLO(path), path
    return YOLO("best-5.pt"), "best-5.pt (fallback - no custom weights found)"

model, active_weights_path = load_yolo_model(CANDIDATE_WEIGHTS)

ALERT_KEYWORDS = ["fall", "fallen", "down", "lying", "faint", "collapse"]
model_class_names = model.names 

ALERT_CLASS_IDS = {
    idx for idx, name in model_class_names.items()
    if any(kw in str(name).lower() for kw in ALERT_KEYWORDS)
}
ALERT_ON_ANY_DETECTION = len(ALERT_CLASS_IDS) == 0

# --- 4. GLOBAL STYLE INJECTION ---
css_template = """
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&family=JetBrains+Mono:wght=400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --surface-container-lowest: [surface_container_lowest];
            --surface-container-low: [surface_container_low];
            --surface-container: [surface_container];
            --surface-container-high: [surface_container_high];
            --on-surface: [on_surface];
            --on-surface-variant: [on_surface_variant];
            --outline: [outline];
            --outline-variant: [outline_variant];
            --primary: [primary];
            --secondary: [secondary];
            --tertiary: [tertiary];
            --emergency-red: [emergency_red];
            --sp-base: [sp_base]px;
            --sp-xs: [sp_xs]px;
            --sp-sm: [sp_sm]px;
            --sp-md: [sp_md]px;
            --radius-default: [radius_default]px;
            --radius-lg: [radius_lg]px;
            --radius-full: [radius_full]px;
        }

        .stApp { background-color: var(--surface-container-lowest); color: var(--on-surface); font-family: 'Inter', sans-serif; }
        div[data-testid="stHeader"] { background: transparent; }
        .block-container { padding-top: var(--sp-sm) !important; }
        [data-testid="stSidebar"] { background-color: var(--surface-container-low); border-right: 1px solid var(--outline-variant); }

        .mono { font-family: 'JetBrains Mono', monospace; }
        .label-caps {
            font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 500;
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--on-surface-variant);
        }
        .data-mono { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: var(--secondary); }

        .glass-panel {
            background: var(--surface-container) !important;
            border: 1px solid var(--outline-variant) !important;
            padding: var(--sp-sm); border-radius: var(--radius-lg); position: relative;
        }

        .accent-bar { position: absolute; top: 0; left: 0; bottom: 0; width: 2px; border-radius: var(--radius-default) 0 0 var(--radius-default); }
        .accent-bar.ok { background: var(--secondary); }
        .accent-bar.alert { background: var(--emergency-red); }

        .live-feed-container {
            position: relative; background: #000; border-radius: var(--radius-lg);
            overflow: hidden; border: 1px solid var(--outline-variant);
        }
        .scanning-line {
            position: absolute; top: 0; left: 0; width: 100%; height: 1px; background: var(--secondary);
            box-shadow: 0 0 12px rgba(78, 222, 163, 0.3); animation: scan 4s linear infinite;
            pointer-events: none; z-index: 10;
        }
        @keyframes scan { 0% { top: 0; } 100% { top: 100%; } }

        .status-pill {
            background: rgba(78, 222, 163, 0.1); border: 1px solid rgba(78, 222, 163, 0.25); color: var(--secondary);
            padding: var(--sp-base) var(--sp-xs); border-radius: var(--radius-full);
            font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500; letter-spacing: 0.05em;
            display: inline-flex; align-items: center; gap: var(--sp-base);
        }

        .zone-row {
            display: flex; align-items: center; gap: var(--sp-sm); padding: var(--sp-xs) var(--sp-sm);
            border-radius: var(--radius-default); background: rgba(255,255,255,0.03);
            border: 1px solid var(--outline-variant); margin-bottom: var(--sp-xs);
        }
        .zone-row.alert { border-color: var(--emergency-red); background: rgba(239, 68, 68, 0.08); }

        .progress-track { width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: var(--radius-full); overflow: hidden; }
        .progress-fill { height: 100%; border-radius: var(--radius-full); }

        .stButton > button { border-radius: var(--radius-lg) !important; font-weight: 600 !important; border: 1px solid var(--outline-variant) !important; }
        .stButton > button[kind="primary"] { background-color: var(--emergency-red) !important; border-color: var(--emergency-red) !important; color: #fff !important; }
        
        hr { border-color: var(--outline-variant) !important; opacity: 0.4; }
    </style>
"""

for key, val in T.items():
    css_template = css_template.replace(f"[{key}]", str(val))
for key, val in SPACE.items():
    css_template = css_template.replace(f"[sp_{key}]", str(val))
for key, val in RADIUS.items():
    css_template = css_template.replace(f"[radius_{key}]", str(val))

st.markdown(css_template, unsafe_allow_html=True)

# --- 5. TOP NAVIGATION BAR ---
st.markdown(f"""
    <nav class="glass-panel" style="display:flex; justify-content:space-between; align-items:center;
         padding:{SPACE['xs']}px {SPACE['md']}px; margin-bottom:{SPACE['md']}px;">
        <div style="display:flex; align-items:center; gap:{SPACE['xs']}px;">
            <span class="pulse-dot"></span>
            <span style="font-size:20px; font-weight:700; letter-spacing:-0.01em; color:{T['on_surface']};">LifeGuard AI</span>
            <span class="label-caps" style="margin-left:{SPACE['base']}px;">Clinical Intelligence</span>
        </div>
        <div class="status-pill">CLOUD BROADCAST ACTIVE</div>
    </nav>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown('<span class="status-pill">CAMERA CONFIG</span>', unsafe_allow_html=True)
    st.markdown(f"<div style='height:{SPACE['sm']}px'></div>", unsafe_allow_html=True)
    st.markdown("<p class='label-caps' style='margin-bottom:0;'>Settings Panel</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin-top:{SPACE['base']}px;'>Inference Tuning</h3>", unsafe_allow_html=True)

    st.markdown(f"<p class='mono' style='font-size:11px; color:{T['secondary']};'>MODEL: {active_weights_path}</p>", unsafe_allow_html=True)
    
    confidence_threshold = st.slider("AI Sensitivity (Confidence)", 0.0, 1.0, 0.45)
    
    st.info("💡 Click 'Start' inside the video monitor window to turn on your local browser webcam feed stream.")

# --- 7. MAIN LAYOUT GRID ---
col_main, col_intel = st.columns([2, 1])

with col_main:
    st.markdown(f"<h2 style='color:{T['on_surface']}; margin:0; font-size:24px; font-weight:700; letter-spacing:-0.01em;'>Live Monitor</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='mono' style='color:{T['outline']}; font-size:12px; margin-top:{SPACE['base']}px;'>SOURCE: LOCAL WEBRTC BROWSER CAMERA</p>", unsafe_allow_html=True)

    # --- WebRTC Processing Core Engine ---
    class VideoTransformer(VideoProcessorBase):
        def __init__(self):
            self.model = model
            self.conf = confidence_threshold

        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # Run Live Inference Frame By Frame
            results = self.model(img, conf=self.conf, verbose=False)
            annotated_frame = results[0].plot()
            
            return frame.from_ndarray(annotated_frame, format="bgr24")

    # Interactive video display panel
    st.markdown('<div class="live-feed-container"><div class="scanning-line"></div>', unsafe_allow_html=True)
    
    webrtc_streamer(
        key="lifeguard-stream",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
        video_processor_factory=VideoTransformer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_intel:
    st.markdown(f"<p class='label-caps' style='margin-bottom:{SPACE['xs']}px;'>Intelligence Feed</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="zone-row"><div style="flex:1;">
            <p style="margin:0; font-size:12px; font-weight:700; color:{T['on_surface']};">STUN RELAY NODE</p>
            <p class="mono" style="margin:0; font-size:10px; color:{T['secondary']};">STATUS // WEBRTC TUNNEL STABLE</p>
        </div></div>
    """, unsafe_allow_html=True)
    
    log_box = st.container(height=280, border=True)
    with log_box:
        st.markdown("".join(st.session_state.logs), unsafe_allow_html=True)
