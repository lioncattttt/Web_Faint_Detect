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

        .stButton > button {{ border-radius: var(--radius-lg) !important; font-weight: 600 !important; border: 1px solid var(--outline-variant) !important; }}
        .stButton > button[kind="primary"] {{ background-color: var(--emergency-red) !important; border-color: var(--emergency-red) !important; color: #fff !important; }}
        .stButton > button[kind="primary"]:hover {{ box-shadow: 0 0 16px rgba(239, 68, 68, 0.45) !important; }}

        [data-testid="stSlider"] [role="slider"] {{ background-color: var(--tertiary) !important; }}
        [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{ background: var(--tertiary) !important; }}

        hr {{ border-color: var(--outline-variant) !important; opacity: 0.4; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. TOP NAVIGATION BAR ---
st.markdown(f"""
    <nav class="glass-panel" style="display:flex; justify-content:space-between; align-items:center;
         padding:{SPACE['xs']}px {SPACE['md']}px; margin-bottom:{SPACE['md']}px;">
        <div style="display:flex; align-items:center; gap:{SPACE['xs']}px;">
            <span class="pulse-dot"></span>
            <span style="font-size:20px; font-weight:700; letter-spacing:-0.01em; color:{T['on_surface']};">LifeGuard AI</span>
            <span class="label-caps" style="margin-left:{SPACE['base']}px;">Clinical Intelligence</span>
        </div>
        <div class="status-pill"><span class="pulse-dot"></span>SYSTEM CORE ONLINE</div>
    </nav>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown('<span class="status-pill">CAMERA CONFIG</span>', unsafe_allow_html=True)
    st.markdown(f"<div style='height:{SPACE['sm']}px'></div>", unsafe_allow_html=True)
    st.markdown("<p class='label-caps' style='margin-bottom:0;'>Settings Panel</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin-top:{SPACE['base']}px;'>Inference Tuning</h3>", unsafe_allow_html=True)

    weights_color = T["secondary"] if active_weights_path in ("best.pt", "best-4.pt") else T["tertiary"]
    st.markdown(f"<p class='mono' style='font-size:11px; color:{weights_color};'>MODEL: {active_weights_path}</p>", unsafe_allow_html=True)
    
    if active_weights_path not in ("best.pt", "best-4.pt"):
        st.caption("Drop best.pt next to this script to use your trained weights.")

    with st.expander("Model classes / alert logic", expanded=False):
        st.markdown(f"<p class='mono' style='font-size:11px; color:{T['on_surface_variant']};'>{model_class_names}</p>", unsafe_allow_html=True)
        if ALERT_ON_ANY_DETECTION:
            st.markdown(f"<p class='mono' style='font-size:11px; color:{T['tertiary']};'>No class names matched fall/down keywords — treating ANY detection as an alert.</p>", unsafe_allow_html=True)
        else:
            alert_names = [str(model_class_names[i]) for i in ALERT_CLASS_IDS]
            st.markdown(f"<p class='mono' style='font-size:11px; color:{T['secondary']};'>Alerting only on: {', '.join(alert_names)}</p>", unsafe_allow_html=True)

    confidence_threshold = st.slider("AI Sensitivity (Confidence)", 0.0, 1.0, 0.45)

    st.divider()
    source_type = st.radio("Target Input Source", ["Camera/Phone Stream", "Demo File Corridor"])

    video_path = 0
    if source_type == "Camera/Phone Stream":
        # Updated: Accepts either a basic digit index (0, 1) or a phone IP webcam URL
        camera_input = st.text_input(
            "Receiver Address / Source", 
            value="0", 
            help="Enter '0' for built-in camera, or an IP stream URL like 'http://192.168.1.50:8080/video' if streaming from your phone."
        )
        if camera_input.isdigit():
            video_path = int(camera_input)
        else:
            video_path = camera_input
    else:
        uploaded_video = st.file_uploader("Upload a demo video file", type=["mp4", "mov", "avi", "mkv"])
        if uploaded_video is not None:
            demo_path = os.path.join("/tmp", "lifeguard_demo_upload.mp4")
            with open(demo_path, "wb") as f:
                f.write(uploaded_video.read())
            video_path = demo_path
        else:
            video_path = "demo_corridor.mp4"
            st.caption("No file uploaded - will try demo_corridor.mp4 in the working directory.")

    run_stream = st.checkbox("📡 START MONITOR FEED", value=False)

    st.divider()
    if st.button("🚨 PANIC: TRIGGER ALERT", use_container_width=True, type="primary"):
        st.toast("⚠️ EMERGENCY DESK TRANSMISSION CONFIRMED!")

# --- 7. MAIN LAYOUT GRID ---
col_main, col_intel = st.columns([2, 1])

with col_main:
    header_l, header_r = st.columns([2, 1])
    with header_l:
        st.markdown(f"<h2 style='color:{T['on_surface']}; margin:0; font-size:24px; font-weight:700; letter-spacing:-0.01em;'>Live Monitor</h2>", unsafe_allow_html=True)
        st.markdown(f"<p class='mono' style='color:{T['outline']}; font-size:12px; margin-top:{SPACE['base']}px;'>ZONE: CORRIDOR B-42 // CAMERA: NORTH_084</p>", unsafe_allow_html=True)
    with header_r:
        clock_slot = st.empty()

    st.markdown('<div class="live-feed-container"><div class="scanning-line"></div>', unsafe_allow_html=True)
    badge_slot = st.empty()
    image_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<div style='height:{SPACE['sm']}px'></div>", unsafe_allow_html=True)

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.markdown('<div class="glass-panel"><div class="accent-bar ok"></div><p class="label-caps" style="margin:0;">Processing Speed</p>', unsafe_allow_html=True)
        metric_fps = st.empty()
        bar_fps = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
    with stat_col2:
        st.markdown('<div class="glass-panel"><div class="accent-bar ok"></div><p class="label-caps" style="margin:0;">Tracked Anomalies</p>', unsafe_allow_html=True)
        metric_count = st.empty()
        bar_count = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
    with stat_col3:
        st.markdown('<div class="glass-panel"><div class="accent-bar ok"></div><p class="label-caps" style="margin:0;">Network Precision</p>', unsafe_allow_html=True)
        metric_conf = st.empty()
        bar_conf = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)

with col_intel:
    st.markdown(f"<p class='label-caps' style='margin-bottom:{SPACE['xs']}px;'>Intelligence Feed</p>", unsafe_allow_html=True)
    zone_slot = st.empty()
    log_box = st.container(height=360, border=True)

# Helper Rendering Functions
def stamp():
    return datetime.now().strftime("%H:%M:%S")

def render_metric(slot, value, color):
    slot.markdown(f"<h3 style='margin:0; font-family:\"JetBrains Mono\", monospace; color:{color};'>{value}</h3>", unsafe_allow_html=True)

def render_bar(slot, pct, color):
    pct = max(0, min(100, pct))
    slot.markdown(f"<div class='progress-track'><div class='progress-fill' style='width:{pct}%; background:{color};'></div></div>", unsafe_allow_html=True)

def render_zone_status(slot, person_present, alert):
    sub, cls = ("ALERT // PERSON DOWN DETECTED", "alert") if alert else (("ACTIVE // PERSON DETECTED", "ok") if person_present else ("MONITORING // NO ACTIVITY", "ok"))
    row_class = "zone-row alert" if cls == "alert" else "zone-row"
    text_color = T["emergency_red"] if cls == "alert" else T["secondary"]
    slot.markdown(f"<div class='{row_class}'><div style='flex:1;'><p style='margin:0; font-size:12px; font-weight:700; color:{T['on_surface']};'>CORRIDOR B-42</p><p class='mono' style='margin:0; font-size:10px; color:{text_color};'>{sub}</p></div></div>", unsafe_allow_html=True)

def render_badge(slot, alert):
    if alert:
        slot.markdown(f"<div class='ai-active-badge alert'><span class='pulse-dot alert'></span><span class='mono' style='font-size:11px; color:{T['emergency_red']}; font-weight:700;'>ANOMALY DETECTED</span></div>", unsafe_allow_html=True)
    else:
        slot.markdown(f"<div class='ai-active-badge'><span class='pulse-dot'></span><span class='mono' style='font-size:11px; color:{T['secondary']}; font-weight:700;'>AI ANALYTICS ACTIVE</span></div>", unsafe_allow_html=True)

def update_logs_display():
    with log_box:
        st.markdown("".join(st.session_state.logs), unsafe_allow_html=True)

# Initial baseline rendering
clock_slot.markdown(f"<p class='mono' style='text-align:right; font-size:11px; color:{T['outline']};'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
render_metric(metric_fps, "0.0 FPS", T["secondary"])
render_bar(bar_fps, 0, T["secondary"])
render_metric(metric_count, "0 Active", T["secondary"])
render_bar(bar_count, 0, T["secondary"])
render_metric(metric_conf, f"{confidence_threshold*100:.1f}%", T["tertiary"])
render_bar(bar_conf, confidence_threshold * 100, T["tertiary"])
render_badge(badge_slot, alert=False)
render_zone_status(zone_slot, person_present=False, alert=False)
update_logs_display()

# --- 8. LIVE CAPTURE LOOP ---
if run_stream:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error(f"Cannot open video source `{video_path}`. Verify the address link or standard camera index.")
    else:
        prev_time = time.time()
        frame_counter = 0

        while cap.isOpened() and run_stream:
            ret, frame = cap.read()
            if not ret:
                if source_type == "Demo File Corridor":
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                st.warning("Lost connection to camera feed.")
                break

            frame_counter += 1
            frame = cv2.resize(frame, (854, 480))

            # Inference execution
            results = model(frame, conf=confidence_threshold, verbose=False)
            boxes = results[0].boxes
            detections = len(boxes)
            annotated_frame = results[0].plot()

            if ALERT_ON_ANY_DETECTION:
                alert_count = detections
            else:
                alert_count = sum(1 for c in boxes.cls.tolist() if int(c) in ALERT_CLASS_IDS)
            alert_active = alert_count > 0

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            image_placeholder.image(annotated_frame, channels="BGR", use_container_width=True)

            if frame_counter % 6 == 0:
                clock_slot.markdown(f"<p class='mono' style='text-align:right; font-size:11px; color:{T['outline']};'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
                render_badge(badge_slot, alert=alert_active)
                render_zone_status(zone_slot, person_present=detections > 0, alert=alert_active)

                fps_color = T["secondary"] if fps >= 15 else T["tertiary"]
                render_metric(metric_fps, f"{fps:.1f} FPS", fps_color)
                render_bar(bar_fps, min(fps / 30 * 100, 100), fps_color)

                count_color = T["emergency_red"] if alert_active else T["secondary"]
                render_metric(metric_count, f"{alert_count} Active", count_color)
                render_bar(bar_count, min(alert_count * 25, 100), count_color)

                render_metric(metric_conf, f"{confidence_threshold*100:.1f}%", T["tertiary"])
                render_bar(bar_conf, confidence_threshold * 100, T["tertiary"])

            if alert_active and frame_counter % 24 == 0:
                new_log = f"<p class='mono' style='color:{T['emergency_red']}; font-size:12px; margin:2px 0;'>⚠ [ALERT] {alert_count} signature flag(s) - Camera NORTH_084 - {stamp()}</p>"
                st.session_state.logs.append(new_log)
                update_logs_display()

            time.sleep(0.01)
        cap.release()
else:
    image_placeholder.image(
        "https://images.unsplash.com/photo-1516733725897-1aa73b87c8e8?auto=format&fit=crop&q=80&w=2070",
        use_container_width=True
    )
