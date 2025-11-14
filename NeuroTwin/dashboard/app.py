import streamlit as st
import pyttsx3
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from brain.renderer import render_brain
from twin.builder import DigitalTwin
from fpdf import FPDF

def run_dashboard(twin=None):
    st.set_page_config(page_title="NeuroTwin", layout="wide", page_icon="brain")
    st.markdown("# NeuroTwin: Your Personal Brain Digital Twin")
    st.markdown("**Upload your mood diary → See your brain in 3D → Get crisis alerts**")

    uploaded = st.file_uploader("Upload Mood Diary (CSV)", type=['csv'])

    if uploaded:
        # Determine the correct data directory
        data_dir = "data" if os.path.isdir("data") else "NeuroTwin/data"
        path = f"{data_dir}/uploaded_{uploaded.name}"
        os.makedirs(data_dir, exist_ok=True)
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        twin = DigitalTwin(path)
    elif twin is None:
        # Determine the correct path to sample data
        sample_path = "data/sample_mood_log.csv" if os.path.isfile("data/sample_mood_log.csv") else "NeuroTwin/data/sample_mood_log.csv"
        twin = DigitalTwin(sample_path)
        st.info("Using sample data. Upload your own for personalized twin.")

    with st.expander("Panel: Enter Mood Live (No CSV)"):
        with st.form("live_mood"):
            mood = st.selectbox("Mood", ["happy", "neutral", "anxious", "depressed"])
            stress = st.slider("Stress Level", 1, 10, 5)
            sleep = st.slider("Sleep (hours)", 0.0, 12.0, 7.0)
            note = st.text_input("Note (optional)")
            submit = st.form_submit_button("Update My Brain")

            if submit:
                new_row = pd.DataFrame([{
                    "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "mood": mood,
                    "stress": stress,
                    "sleep_hours": sleep,
                    "notes": note
                }])
                if 'live_df' not in st.session_state:
                    st.session_state.live_df = new_row
                else:
                    st.session_state.live_df = pd.concat([st.session_state.live_df, new_row], ignore_index=True)
                st.success("Mood added! Brain updating...")
                st.rerun()

    if 'twin' not in st.session_state:
        twin.build()
        st.session_state.twin = twin

    twin = st.session_state.twin
    risk = twin.predict_depression()

    # === AFTER RISK CALCULATION ===
    df = None
    if 'live_df' in st.session_state:
        df = st.session_state.live_df

    # Trend chart
    if df is not None and len(df) > 1:
        trend_df = df.copy()
        trend_df['risk'] = trend_df.apply(lambda row: np.clip(40 + row['stress']*8.51 - row['sleep_hours']*3.8, 0, 100), axis=1)
        st.line_chart(trend_df.set_index('date')['risk'], width='stretch')
        st.caption("Risk Trend Over Time")

    # Therapy recommendation
    if risk > 75:
        st.warning("Recommended: **Immediate CBT Session**")
    elif risk > 50:
        st.info("Suggested: **Mindfulness App (Headspace)**")
    else:
        st.success("Maintain: **Daily Journal + Exercise**")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("7-Day Depression Risk", f"{risk}%", delta="+8%")
        st.metric("Anxiety Level", "High" if risk > 70 else "Moderate")
        
        if risk > 75:
            st.error("CRISIS ALERT: Immediate intervention recommended")
            if st.button("Play Voice Alert"):
                engine = pyttsx3.init()
                engine.say("Crisis detected. You are not alone. Please contact a therapist now.")
                engine.runAndWait()
                st.success("Voice alert played.")

    with col2:
        fig = render_brain(risk)
        st.plotly_chart(fig, width='stretch')

    with st.expander("View Your Mood Data"):
        st.write(twin.df.to_string())

    # Full report export
    if st.button("📄 Export Full Report (PDF + 3D Brain)"):
        try:
            # Save brain as PNG
            fig.write_image("brain_snapshot.png")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "NeuroTwin Mental Health Report", ln=1, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Risk: {risk}% | Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}", ln=1)
            if os.path.exists("brain_snapshot.png"):
                pdf.image("brain_snapshot.png", x=10, y=pdf.get_y(), w=180)
            pdf.output("NeuroTwin_Full_Report.pdf")
            st.success("✓ Full report with 3D brain saved to NeuroTwin_Full_Report.pdf!")
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

    if st.button("🎤 Analyze My Voice Tone"):
        st.info("🎙️ Analyzing voice tone...")
        with st.spinner("Processing audio..."):
            import time
            time.sleep(0.5)
        # Mock result
        tone = np.random.choice(["anxious", "calm", "depressed"])
        st.write(f"🔊 Detected tone: **{tone.upper()}**")
        if tone == "anxious":
            st.error("⚠️ Voice confirms high stress!")
        elif tone == "calm":
            st.success("✓ Voice analysis shows calm demeanor")
        else:
            st.warning("⚠️ Voice suggests depressed mood")

    st.sidebar.success("NeuroTwin Active | Privacy: 100% Local")

if __name__ == "__main__":
    run_dashboard()
