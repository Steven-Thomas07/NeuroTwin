import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pyttsx3
from fpdf import FPDF  # Fixed import
import streamlit.components.v1 as components
from datetime import datetime
import os

# Page Config
st.set_page_config(page_title="NeuroTwin", layout="wide", page_icon="🧠")
st.markdown("# 🧠 NeuroTwin: Your Personal Brain Digital Twin")
st.markdown("**Upload CSV → Speak → See 3D Brain → Get Crisis Alert**")

# Initialize Session State
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["date", "mood", "stress", "sleep_hours", "notes"])
if 'risk' not in st.session_state:
    st.session_state.risk = 0

# === 1. CSV UPLOADER ===
uploaded_file = st.file_uploader("**Upload Mood Diary (CSV)**", type=['csv'])

if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        required_cols = ["date", "mood", "stress", "sleep_hours"]
        if not all(col in df_upload.columns for col in required_cols):
            st.error("CSV must have: date, mood, stress, sleep_hours")
        else:
            st.session_state.df = df_upload[required_cols + ["notes"] if "notes" in df_upload.columns else required_cols].copy()
            st.success(f"Loaded {len(st.session_state.df)} entries!")
            st.rerun()
    except Exception as e:
        st.error(f"Invalid CSV: {e}")

# === 2. LIVE MOOD FORM ===
with st.expander("**Or Enter Mood Live**"):
    with st.form("live_mood_form"):
        col1, col2 = st.columns(2)
        with col1:
            mood = st.selectbox("Mood", ["happy", "neutral", "anxious", "depressed"])
            stress = st.slider("Stress (1-10)", 1, 10, 5)
        with col2:
            sleep = st.slider("Sleep (hours)", 0.0, 12.0, 7.0, 0.1)
            note = st.text_input("Note (optional)")
        submit = st.form_submit_button("Add to Diary")

        if submit:
            new_row = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mood": mood,
                "stress": stress,
                "sleep_hours": sleep,
                "notes": note
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success("Mood added! Brain updating...")
            st.rerun()

# === 3. DATAFRAME (Always Use Session State) ===
df = st.session_state.df
if df.empty:
    df = pd.DataFrame({
        "date": ["2025-11-08", "2025-11-09"],
        "mood": ["happy", "anxious"],
        "stress": [3.0, 8.0],
        "sleep_hours": [8.0, 4.0],
        "notes": ["Good day", "Stressed"]
    })
    st.info("Using sample data. Upload CSV or add live mood.")
else:
    st.write("**Your Mood Data:**")
    st.dataframe(df, use_container_width=True)

# === 4. RISK CALCULATION ===
def calculate_risk(df):
    try:
        avg_stress = df['stress'].mean()
        avg_sleep = df['sleep_hours'].mean()
        risk = np.clip(40 + (avg_stress * 6.2) - (avg_sleep * 3.8), 0, 100)
        return round(risk, 1), avg_stress, avg_sleep
    except:
        return 0, 0, 0

risk, avg_stress, avg_sleep = calculate_risk(df)
st.session_state.risk = risk

# === 5. 3D BRAIN RENDERER ===
def render_brain(risk):
    regions = ["Prefrontal Cortex", "Amygdala (Anxiety)", "Hippocampus"]
    x, y, z = [0, 1, 2], [0, 1, 0], [0, 0, 1]
    colors = ['green', 'red' if risk > 70 else 'yellow', 'blue']
    sizes = [15, 28 if risk > 70 else 20, 14]
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+text+lines',
        marker=dict(size=sizes, color=colors),
        text=regions,
        textposition="top center",
        line=dict(color='gray', width=3),
        hovertemplate='<b>%{text}</b><br>Risk: %{customdata:.1f}%<extra></extra>',
        customdata=[risk*0.3, risk, risk*0.5]
    )])
    fig.update_layout(
        title=f"Brain Activity | Risk: {risk}%",
        scene=dict(xaxis_title='', yaxis_title='', zaxis_title=''),
        height=500,
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

# === 6. LAYOUT ===
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("**7-Day Depression Risk**", f"{risk}%", delta="+12%")
    st.metric("Avg Stress", f"{avg_stress:.1f}/10")
    st.metric("Avg Sleep", f"{avg_sleep:.1f} hrs")

    if risk > 75:
        st.error("**CRISIS ALERT: Seek help now**")
        if st.button("🔊 Play Voice Alert"):
            try:
                engine = pyttsx3.init()
                engine.say("Crisis detected. You are not alone. Contact a therapist now.")
                engine.runAndWait()
                st.success("Alert played!")
            except:
                st.warning("Voice not supported. Text alert shown.")
    elif risk > 50:
        st.warning("Elevated Risk: Try mindfulness")
    else:
        st.success("Low Risk: Keep it up!")

    if st.button("📄 Export Full Report (PDF)"):
        try:
            fig = render_brain(risk)
            fig.write_image("brain.png")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "NeuroTwin Report", ln=1, align='C')
            pdf.ln(8)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Risk Level: {risk}%", ln=1)
            pdf.cell(0, 10, f"Average Stress: {avg_stress:.1f}/10", ln=1)
            pdf.cell(0, 10, f"Average Sleep: {avg_sleep:.1f} hours", ln=1)
            pdf.ln(5)
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.output("NeuroTwin_Report.pdf")
            
            with open("NeuroTwin_Report.pdf", "rb") as f:
                st.download_button("📥 Download PDF Report", f.read(), "NeuroTwin_Report.pdf", "application/pdf")
            st.success("✅ PDF ready to download!")
        except Exception as e:
            st.error(f"PDF error: {e}")

with col2:
    fig = render_brain(risk)
    st.plotly_chart(fig, use_container_width=True)

# === 7. SIMPLIFIED VOICE ANALYSIS (TEXT-BASED Fallback for Easy Testing) ===
with st.expander("🎙️ **Voice Analysis (Text Simulation for Demo)**"):
    st.info("**For real mic:** Use Chrome + allow permission. For now, type what you'd say.")
    
    speech_text = st.text_area("**Type what you'd say into the mic** (e.g., 'I'm feeling anxious')", "I'm happy today")
    if st.button("Analyze Speech"):
        if speech_text:
            text_lower = speech_text.lower()
            if any(word in text_lower for word in ["anxious", "sad", "depressed", "stress", "bad", "worried", "angry", "frustrated"]):
                emotion = "anxious"
                risk_level = "high"
            elif any(word in text_lower for word in ["happy", "good", "great", "calm", "relaxed", "excited"]):
                emotion = "happy"
                risk_level = "low"
            else:
                emotion = "neutral"
                risk_level = "moderate"

            st.write(f"**Detected Emotion:** {emotion.upper()}")
            st.write(f"**Risk Level:** {risk_level.upper()}")
            
            if risk_level == "high":
                st.error("⚠️ Voice indicates high stress/anxiety")
                # Add to mood data
                new_entry = pd.DataFrame([{
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "mood": "anxious",
                    "stress": 8.0,
                    "sleep_hours": 5.0,
                    "notes": f"Voice: {speech_text}"
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                st.success("Mood data updated from voice!")
                st.rerun()
            else:
                st.success("✅ Voice analysis shows stable mood")
        else:
            st.warning("No speech text. Try again.")

# === 8. RISK TREND CHART ===
if len(df) > 1:
    trend_df = df.copy()
    trend_df['daily_risk'] = trend_df.apply(
        lambda row: np.clip(40 + row['stress']*6.2 - row['sleep_hours']*3.8, 0, 100), axis=1
    )
    st.subheader("Risk Trend Over Time")
    st.line_chart(trend_df.set_index('date')['daily_risk'])

st.sidebar.success("NeuroTwin Active | 100% Local")
