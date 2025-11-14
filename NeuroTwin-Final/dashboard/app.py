import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pyttsx3
from fpdf import FPDF
import streamlit.components.v1 as components
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from twin.builder import DigitalTwin
from brain.renderer import render_brain

st.set_page_config(page_title="NeuroTwin", layout="wide", page_icon="🧠")

st.markdown("# 🧠 NeuroTwin: Your Personal Brain Digital Twin")
st.markdown("**Upload mood diary → See 3D brain → Get crisis alert**")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'risk' not in st.session_state:
    st.session_state.risk = 0
if 'live_df' not in st.session_state:
    st.session_state.live_df = pd.DataFrame()

# File uploader
uploaded_file = st.file_uploader("Upload Mood Diary (CSV)", type=['csv'])

# Process upload
if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success("CSV uploaded! Analyzing new data...")
        st.rerun()
    except Exception as e:
        st.error(f"CSV error: {e}. Expected columns: date, mood, stress, sleep_hours, notes")
        st.session_state.df = None

# Live mood form
with st.expander("Or Enter Mood Live (No CSV Needed)"):
    with st.form("live_mood"):
        mood = st.selectbox("Mood", ["happy", "neutral", "anxious", "depressed"])
        stress = st.slider("Stress (1-10)", 1, 10, 5)
        sleep = st.slider("Sleep (hours)", 0.0, 12.0, 7.0)
        note = st.text_input("Note")
        submit = st.form_submit_button("Add to Diary")

        if submit:
            new_row = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mood": mood,
                "stress": stress,
                "sleep_hours": sleep,
                "notes": note
            }])
            st.session_state.live_df = pd.concat([st.session_state.live_df, new_row], ignore_index=True)
            st.success("Mood added! Updating brain...")
            st.rerun()

# Use live or uploaded data
df = st.session_state.live_df if not st.session_state.live_df.empty else st.session_state.df

# Sample data if none
if df is None or df.empty:
    df = pd.DataFrame({
        "date": ["2025-11-08", "2025-11-09", "2025-11-10"],
        "mood": ["happy", "anxious", "neutral"],
        "stress": [3.2, 7.8, 4.1],
        "sleep_hours": [7.5, 5.2, 6.8],
        "notes": ["good day", "work stress", "normal"]
    })
    st.info("Using sample data. Upload CSV or enter live mood.")

# Build twin and calculate risk
twin = DigitalTwin(df)
risk = twin.build()
st.session_state.risk = risk

# 3D Brain
def render_brain(risk):
    regions = ["Prefrontal Cortex", "Amygdala (Anxiety)", "Hippocampus (Memory)"]
    x = [0, 1, 2]
    y = [0, 1, 0]
    z = [0, 0, 1]
    colors = ['green', 'red' if risk > 70 else 'yellow', 'blue']
    sizes = [15, 25 if risk > 70 else 18, 12]
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+text+lines',
        marker=dict(size=sizes, color=colors),
        text=regions,
        textposition="top center",
        line=dict(color='gray', width=3),
        hovertemplate='<b>%{text}</b><br>Risk Impact: %{customdata:.1f}%<extra></extra>',
        customdata=[risk * 0.3, risk, risk * 0.5]
    )])
    fig.update_layout(
        title=f"Brain Digital Twin | Risk: {risk:.1f}%",
        scene=dict(xaxis_title='Left → Right', yaxis_title='Front → Back', zaxis_title='Bottom → Top'),
        height=500
    )
    return fig

# Layout
col1, col2 = st.columns([1, 2])
with col1:
    st.metric("7-Day Depression Risk", f"{risk:.1f}%", delta="+12%")
    st.metric("Avg Stress", f"{df['stress'].mean():.1f}/10")
    st.metric("Avg Sleep", f"{df['sleep_hours'].mean():.1f} hrs")

    if risk > 75:
        st.error("CRISIS ALERT: Seek immediate help")
        if st.button("Play Voice Alert"):
            try:
                engine = pyttsx3.init()
                engine.say("Crisis detected. You are not alone. Please contact a therapist immediately.")
                engine.runAndWait()
                st.success("Voice alert played!")
            except Exception as e:
                st.warning(f"Voice error: {e}. Text alert: 'Contact therapist now!'")
    elif risk > 50:
        st.warning("Elevated Risk: Consider mindfulness app")
    else:
        st.success("Low Risk: Maintain healthy habits")

    st.info("Therapy Rec: Daily journaling + exercise")

with col2:
    fig = render_brain(risk)
    st.plotly_chart(fig, use_container_width=True)

# Trend chart
if len(df) > 1:
    trend_df = df.copy()
    trend_df['daily_risk'] = trend_df.apply(lambda row: np.clip(40 + row['stress']*6.2 - row['sleep_hours']*3.8, 0, 100), axis=1)
    st.subheader("Risk Trend Over Time")
    st.line_chart(trend_df.set_index('date')['daily_risk'])

# Data table
st.subheader("Your Mood Data")
st.dataframe(df)

# PDF export
if st.button("Download Full Report (PDF + Brain Image)"):
    try:
        # Save brain image
        fig.write_image("brain.png")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "NeuroTwin Report", ln=1, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Risk: {risk:.1f}%", ln=1)
        pdf.cell(0, 10, f"Avg Stress: {df['stress'].mean():.1f}", ln=1)
        pdf.cell(0, 10, f"Avg Sleep: {df['sleep_hours'].mean():.1f} hrs", ln=1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
        pdf.ln(5)
        pdf.image("brain.png", x=10, y=pdf.get_y(), w=180)
        pdf.output("NeuroTwin_Report.pdf")
        
        # Download button
        with open("NeuroTwin_Report.pdf", "rb") as f:
            st.download_button("Download PDF", f.read(), file_name="NeuroTwin_Report.pdf")
        st.success("Report generated and ready for download!")
    except Exception as e:
        st.error(f"Report error: {e}. Install kaleido/fpdf2 if missing.")

# Real Mic Input
with st.expander("🎤 Real Mic Input (Voice Sentiment Analysis)"):
    st.info("Click 'Speak Now' → Allow mic → Say your mood. Works in Chrome.")
    
    # HTML for Web Speech API
    speech_html = """
    <div id="transcript"></div>
    <button id="startBtn" onclick="startRecognition()">Speak Now</button>
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    function startRecognition() {
        recognition.start();
        document.getElementById('startBtn').innerHTML = 'Listening...';
        document.getElementById('startBtn').disabled = true;
    }
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('transcript').innerHTML = '<strong>Transcribed:</strong> ' + transcript;
        document.getElementById('startBtn').innerHTML = 'Speak Again';
        document.getElementById('startBtn').disabled = false;
        
        // Send to Streamlit (simulate with text input)
        parent.document.querySelector('iframe').contentWindow.postMessage({
            type: 'speech_result',
            text: transcript
        }, '*');
    };
    
    recognition.onerror = function(event) {
        document.getElementById('transcript').innerHTML = 'Error: ' + event.error;
        document.getElementById('startBtn').innerHTML = 'Speak Now';
        document.getElementById('startBtn').disabled = false;
    };
    </script>
    """
    components.html(speech_html, height=150)
    
    # Fallback text input for transcription
    speech_input = st.text_input("Transcribed Text (or type if mic fails)", "I'm feeling anxious")
    if st.button("Analyze Speech"):
        if speech_input:
            sentiment_words = ["anxious", "sad", "depressed", "stressed"]
            sentiment = "high" if any(word in speech_input.lower() for word in sentiment_words) else "low"
            st.write(f"**Detected Sentiment:** {sentiment.upper()}")
            
            # Update risk from speech
            speech_stress = 8 if sentiment == "high" else 3
            speech_sleep = 4 if sentiment == "high" else 8
            speech_risk = np.clip(40 + speech_stress * 6.2 - speech_sleep * 3.8, 0, 100)
            st.metric("Speech-Triggered Risk", f"{int(speech_risk)}%")
            
            if sentiment == "high":
                st.error("Voice shows high stress! Update diary.")
            else:
                st.success("Voice shows calm mood.")
        else:
            st.warning("No speech. Try again.")

st.sidebar.success("NeuroTwin Active | 100% Local")

# Log update
with open("logs/neurotwin.log", "a") as f:
    f.write(f"{datetime.now()}: Risk {risk:.1f}% from {len(df)} entries\n")
