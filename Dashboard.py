import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------
ADMIN_PASSWORD = "admin123"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔒 Admin Login")
    password = st.text_input("Enter Admin Password:", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("✅ Login successful! Please wait…")
            time.sleep(1)  # small delay to show success
            try:
                st.experimental_rerun()
            except:
                pass
        else:
            st.error("❌ Incorrect password")
else:
    # --------------------------------------------------
    # EARTH LOADER
    # --------------------------------------------------
    def show_earth_loader(seconds=2, text="Connecting…"):
        loader = st.empty()
        loader.markdown(f"""
        <style>
        .loader-wrapper {{
          position: fixed; inset: 0; z-index: 9999;
          display: flex; justify-content: center; align-items: center;
          background: radial-gradient(circle at top,#0f172a,#020617);
        }}
        .earth {{ display: flex; flex-direction: column; align-items: center; gap: 1rem; }}
        .earth p {{ color: white; font-size: 1.1rem; letter-spacing: 1px; }}
        .earth-loader {{
          --watercolor:#3f51d9; --landcolor:#9be24f;
          width:8em; height:8em; position:relative; overflow:hidden;
          border-radius:50%; border:2px solid rgba(255,255,255,0.9);
          background: radial-gradient(circle at 30% 30%,#6a78ff,var(--watercolor));
          box-shadow: inset 0.45em 0.45em rgba(255,255,255,.22),
                      inset -0.6em -0.6em rgba(0,0,0,.42),
                      0 0 22px rgba(79,112,255,.4);
        }}
        .earth-loader svg {{ position:absolute; width:8.2em; opacity:.9; }}
        .earth-loader svg:nth-child(1) {{ top:-2.6em; animation:round1 4s infinite linear; }}
        .earth-loader svg:nth-child(2) {{ bottom:-2.8em; animation:round2 4s infinite linear .9s; }}
        .earth-loader svg:nth-child(3) {{ top:-1.8em; animation:round1 4s infinite linear 1.8s; }}

        @keyframes round1 {{
          0% {{ left:-3.5em; opacity:1; }}
          50% {{ left:-8em; opacity:0; }}
          100% {{ left:-3.5em; opacity:1; }}
        }}
        @keyframes round2 {{
          0% {{ left:5.5em; opacity:1; }}
          50% {{ left:-9em; opacity:0; }}
          100% {{ left:5.5em; opacity:1; }}
        }}
        </style>

        <div class="loader-wrapper">
          <div class="earth">
            <div class="earth-loader">
              <svg viewBox="0 0 200 200"><path fill="var(--landcolor)"
                d="M100 35 C138 38,162 68,158 105 C154 142,120 160,100 156
                   C62 152,38 125,42 100 C46 70,70 40,100 35Z"/></svg>
              <svg viewBox="0 0 200 200"><path fill="var(--landcolor)"
                d="M100 45 C132 48,152 78,148 108 C144 138,118 148,100 145
                   C68 142,48 120,52 100 C56 78,72 50,100 45Z"/></svg>
              <svg viewBox="0 0 200 200"><path fill="var(--landcolor)"
                d="M100 40 C130 44,150 72,146 104 C142 136,118 148,100 144
                   C70 140,50 118,54 100 C58 74,74 46,100 40Z"/></svg>
            </div>
            <p>{text}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(seconds)
        loader.empty()

    # --------------------------------------------------
    # RUN LOADER ONCE
    # --------------------------------------------------
    if "loaded" not in st.session_state:
        st.session_state.loaded = False

    if not st.session_state.loaded:
        show_earth_loader(2, "Initializing Air Quality System…")
        st.session_state.loaded = True
        try:
            st.experimental_rerun()
        except:
            pass

    # --------------------------------------------------
    # DASHBOARD TITLE
    # --------------------------------------------------
    st.title("🌍 Smart Aware Air Quality System")
    st.markdown("**Current Air Quality Dashboard**")

    # --------------------------------------------------
    # CSV UPLOAD
    # --------------------------------------------------
    uploaded_file = st.file_uploader("Upload Air Quality CSV (e.g., Bengaluru.csv)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]

        # Detect datetime column
        datetime_col = None
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                datetime_col = col
                df[col] = pd.to_datetime(df[col], errors='coerce')
                break
        if datetime_col is None:
            df["Time"] = pd.date_range(start="2024-01-01", periods=len(df), freq="H")
            datetime_col = "Time"

        # Detect pollutants
        pollutants = [c for c in df.columns if any(p in c.lower() for p in ["pm2", "pm10", "no2", "so2", "o3", "co"])]

        # --------------------------------------------------
        # AQI FUNCTION
        # --------------------------------------------------
        def calculate_aqi(pm25):
            if pm25 <= 30: return 50, "Good", "🌤️"
            if pm25 <= 60: return 100, "Moderate", "⛅"
            if pm25 <= 90: return 150, "Unhealthy for Sensitive Groups", "🌫️"
            if pm25 <= 120: return 200, "Unhealthy", "😷"
            return 300, "Very Unhealthy", "☠️"

        pm25_col = next((c for c in pollutants if "pm2" in c.lower()), None)
        aqi_value = int(df[pm25_col].iloc[-1]) if pm25_col else 75
        aqi_score, aqi_status, aqi_emoji = calculate_aqi(aqi_value)

        # Dynamic background
        bg_color = "#4CAF50" if aqi_score <= 50 else "#FFC107" if aqi_score <= 100 else "#FF7043" if aqi_score <= 150 else "#C62828"
        st.markdown(f"""
        <style>
        body {{
            background: linear-gradient(to bottom, #ffffff, {bg_color});
            transition: background 0.5s ease;
        }}
        </style>
        """, unsafe_allow_html=True)

        # --------------------------------------------------
        # TOP ROW: AQI Globe + Forecast + Thermometer
        # --------------------------------------------------
        col1, col2, col3 = st.columns([1.2, 1.8, 0.8])

        # ---- AQI Globe ----
        with col1:
            st.subheader("Current Air Quality")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=aqi_score,
                title={'text': f"<b>{aqi_status}</b> {aqi_emoji}"},
                gauge={
                    'axis': {'range': [0, 300]},
                    'bar': {'color': bg_color},
                    'steps': [
                        {'range': [0, 50], 'color': '#4CAF50'},
                        {'range': [51, 100], 'color': '#FFC107'},
                        {'range': [101, 150], 'color': '#FF7043'},
                        {'range': [151, 300], 'color': '#C62828'},
                    ],
                },
            ))
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            <style>
            .globe {{
                width: 110px; height: 110px; border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, #ffffff, {bg_color});
                animation: pulse 2s ease-in-out infinite; margin: auto;
                box-shadow: 0 0 25px {bg_color}; position: relative;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity:0.7; }}
                50% {{ transform: scale(1.08); opacity:1; }}
                100% {{ transform: scale(1); opacity:0.7; }}
            }}
            .dot {{ width: 8px; height: 8px; background: {bg_color}; border-radius: 50%;
                    position: absolute; animation: float 3s infinite; }}
            @keyframes float {{
                0% {{ transform: translateY(0px); opacity:1; }}
                50% {{ transform: translateY(-20px); opacity:0.5; }}
                100% {{ transform: translateY(0px); opacity:1; }}
            }}
            </style>
            <div class="globe">
                <div class="dot" style="left: 20px; animation-delay:0s;"></div>
                <div class="dot" style="left: 50px; animation-delay:0.5s;"></div>
                <div class="dot" style="left: 80px; animation-delay:1s;"></div>
            </div>
            <p style="text-align:center; font-weight:600;">Live AQI Indicator</p>
            """, unsafe_allow_html=True)

        # --------------------------------------------------
        # Forecast Cards
        # --------------------------------------------------
        with col2:
            st.subheader("7-Day Forecast")
            forecast = [("Mon", 45), ("Tue", 55), ("Wed", 70),
                        ("Thu", 90), ("Fri", 120), ("Sat", 110), ("Sun", 80)]
            cols = st.columns(7)
            for i, (day, val) in enumerate(forecast):
                status = calculate_aqi(val)[1]
                bg = "#C8E6C9" if val <= 50 else "#FFE0B2" if val <= 100 else "#FFCDD2"
                with cols[i]:
                    st.markdown(
                        f"<div style='background:{bg}; padding:10px; border-radius:10px; text-align:center; box-shadow: 0px 0px 10px {bg};'>"
                        f"<h4>{day}</h4><h3>{val}</h3><p>{status}</p></div>",
                        unsafe_allow_html=True
                    )

        # --------------------------------------------------
        # Thermometer
        # --------------------------------------------------
        with col3:
            st.subheader("AQI Thermometer")
            st.markdown(f"""
            <style>
            .thermo {{ width:40px; height:200px; background:#E0E0E0; border-radius:20px; margin:auto; position:relative; }}
            .fill {{ width:100%; height:{aqi_score/3}%; background:{bg_color}; border-radius:20px; position:absolute; bottom:0;
                     animation: rise 2s forwards; }}
            @keyframes rise {{ from {{ height:0%; }} to {{ height:{aqi_score/3}%; }} }}
            </style>
            <div class="thermo"><div class="fill"></div></div>
            """, unsafe_allow_html=True)

        # --------------------------------------------------
        # Pollutant Chart + Real-time AQI
        # --------------------------------------------------
        col4, col5 = st.columns([2, 1])

        # Pollutant Chart
        with col4:
            st.subheader("Pollutant Concentrations")
            fig = go.Figure()
            for col in pollutants[:4]:
                fig.add_trace(go.Scatter(x=df[datetime_col], y=df[col], mode="lines", name=col))
            fig.update_layout(xaxis_title="Time", yaxis_title="Concentration (µg/m³)", height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Real-time AQI
        with col5:
            st.subheader("🚨 Live AQI Alerts")
            aqi_placeholder = st.empty()
            for _ in range(5):
                aqi_value = max(0, aqi_value + random.randint(-5, 5))
                aqi_score, aqi_status, aqi_emoji = calculate_aqi(aqi_value)
                if aqi_score <= 50:
                    aqi_placeholder.success(f"🟢 {aqi_status} {aqi_emoji} | AQI: {aqi_score}")
                elif aqi_score <= 100:
                    aqi_placeholder.warning(f"🟡 {aqi_status} {aqi_emoji} | AQI: {aqi_score}")
                elif aqi_score <= 150:
                    aqi_placeholder.warning(f"🟠 {aqi_status} {aqi_emoji} | AQI: {aqi_score}")
                elif aqi_score <= 200:
                    aqi_placeholder.error(f"🔴 {aqi_status} {aqi_emoji} | AQI: {aqi_score}")
                else:
                    aqi_placeholder.error(f"☠️ {aqi_status} | AQI: {aqi_score}")
                time.sleep(2)

            st.markdown("""
            <div style="background:#E3F2FD; padding:12px; border-radius:10px;">
                <b>Health Advice:</b>
                <ul>
                    <li>Wear mask if outdoors</li>
                    <li>Avoid heavy exercise</li>
                    <li>Use air purifiers</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Please upload Bengaluru.csv or any Air Quality CSV file to continue.")
