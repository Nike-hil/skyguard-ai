import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os

# Ensure src directory is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.anomaly_detector import AnomalyDetector
from src.explainability import XAIExplainer, SensorHealthTracker
from src.imputer import DataImputer

st.set_page_config(page_title="SkyGuard AI — Glass UI Console", layout="wide", page_icon="🌐")

# Custom Glassmorphism CSS Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #030712 100%);
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .glass-metric {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }
    .badge-healthy {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-alert {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #dc2626;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "detector" not in st.session_state:
    st.session_state.detector = AnomalyDetector()
    st.session_state.explainer = XAIExplainer()
    st.session_state.health_tracker = SensorHealthTracker()
    st.session_state.imputer = DataImputer()
    st.session_state.history = []

# Header Banner
st.markdown("""
<div class="glass-card" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 style="margin:0; font-size: 2rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            SKYGUARD AI // AWS INTELLIGENCE
        </h1>
        <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Real-Time Anomaly Detection, Explainable AI & Autonomous Self-Healing Sensor Mesh
        </p>
    </div>
    <div style="text-align: right;">
        <span class="badge-healthy">EDGE ENGINE ONLINE (ESP32)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🎛️ Live Stream Controls")
streaming = st.sidebar.toggle("Live Telemetry Stream", value=True)
speed = st.sidebar.slider("Sampling Interval", 0.4, 2.0, 0.8)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Live Chaos Injector")
inject_spike = st.sidebar.button("💥 Thermal Spike (+32°C)")
inject_freeze = st.sidebar.button("❄️ Frozen Humidity Sensor")
inject_dropout = st.sidebar.button("🔌 Barometric Out-of-Bounds")

# Generate Simulated AWS Data Point
now = datetime.now().strftime("%H:%M:%S")
temp = round(24.0 + np.sin(time.time() / 10.0) * 4.0 + np.random.normal(0, 0.3), 2)
press = round(1013.0 + np.cos(time.time() / 20.0) * 2.5 + np.random.normal(0, 0.2), 2)
hum = round(58.0 + np.sin(time.time() / 15.0) * 12.0 + np.random.normal(0, 0.6), 2)

if inject_spike:
    temp += 32.5
elif inject_freeze:
    hum = 91.00
elif inject_dropout:
    press = 710.0

raw_reading = {"timestamp": now, "temperature": temp, "pressure": press, "humidity": hum}

# Core Pipeline Inference
detection = st.session_state.detector.predict_reading(raw_reading)
xai = st.session_state.explainer.explain(raw_reading, detection)
health = st.session_state.health_tracker.update_health(detection["is_anomaly"], xai["shap_importance"])
imputed = st.session_state.imputer.impute(raw_reading, detection["is_anomaly"], xai["shap_importance"])

st.session_state.history.append({
    "time": now,
    "temp_raw": temp,
    "temp_corr": imputed["corrected_temperature"],
    "press_raw": press,
    "hum_raw": hum,
    "is_anomaly": detection["is_anomaly"]
})
if len(st.session_state.history) > 35:
    st.session_state.history.pop(0)

df = pd.DataFrame(st.session_state.history)

# Metric Tiles
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="glass-metric">
        <div style="color: #94a3b8; font-size: 0.85rem;">TEMPERATURE (°C)</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #38bdf8;">{temp} °C</div>
        <span class="{'badge-alert' if 'Fault' in health['temperature_status'] else 'badge-healthy'}">{health['temperature_status']}</span>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="glass-metric">
        <div style="color: #94a3b8; font-size: 0.85rem;">PRESSURE (hPa)</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #fbbf24;">{press} hPa</div>
        <span class="{'badge-alert' if 'Fault' in health['pressure_status'] else 'badge-healthy'}">{health['pressure_status']}</span>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="glass-metric">
        <div style="color: #94a3b8; font-size: 0.85rem;">HUMIDITY (%)</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #34d399;">{hum} %</div>
        <span class="{'badge-alert' if 'Fault' in health['humidity_status'] else 'badge-healthy'}">{health['humidity_status']}</span>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="glass-metric">
        <div style="color: #94a3b8; font-size: 0.85rem;">ANOMALY CONFIDENCE</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {'#f43f5e' if detection['is_anomaly'] else '#10b981'};">{int(detection['anomaly_score']*100)}%</div>
        <span class="{'badge-alert' if detection['is_anomaly'] else 'badge-healthy'}">{'ALERT TRIGGERED' if detection['is_anomaly'] else 'NOMINAL'}</span>
    </div>
    """, unsafe_allow_html=True)

# Main Alert / Explainability Section
st.write("")
if detection["is_anomaly"]:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #ef4444;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0; color:#f87171;">⚠️ Anomalous Event Flagged: {detection['root_cause']}</h3>
            <span class="badge-alert">SEVERITY: CRITICAL</span>
        </div>
        <p style="margin: 8px 0 0 0; color: #cbd5e1;"><b>XAI Diagnostic:</b> {xai['reasoning']}</p>
    </div>
    """, unsafe_allow_html=True)

# Charts Section (col_chart is defined right here)
col_chart, col_xai = st.columns([2, 1])

with col_chart:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**Temperature Channel: Raw Ingestion vs AI Self-Healing Reconstruction**")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_raw"], mode="lines+markers", name="Raw Signal", line=dict(color="#38bdf8", width=2)))
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_corr"], mode="lines", name="Self-Healed (Imputed)", line=dict(color="#34d399", dash="dash", width=2)))
    
    anomalies = df[df["is_anomaly"] == True]
    if not anomalies.empty:
        fig.add_trace(go.Scatter(x=anomalies["time"], y=anomalies["temp_raw"], mode="markers", name="Anomaly Flag", marker=dict(color="#f43f5e", size=10, symbol="x")))
        
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_xai:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**SHAP Feature Attribution (Root Cause)**")
    
    shap_df = pd.DataFrame(list(xai["shap_importance"].items()), columns=["Sensor", "Weight"])
    fig_bar = go.Figure(go.Bar(
        x=shap_df["Weight"],
        y=shap_df["Sensor"],
        orientation='h',
        marker=dict(color=['#38bdf8', '#fbbf24', '#34d399'])
    ))
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(range=[0, 1])
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Live auto-refresh
if streaming:
    time.sleep(speed)
    st.rerun()