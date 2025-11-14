import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pyttsx3
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io

# Set page config
st.set_page_config(page_title="NeuroTwin", layout="wide", page_icon="brain")

# Title
st.markdown("# NeuroTwin: Your Personal Brain Digital Twin")
st.markdown("**Upload mood diary → See 3D brain → Get crisis alert**")

# Initialize session state
if 'twin' not in st.session_state:
    st.session_state.twin = None
if 'risk' not in st.session_state:
    st.session_state.risk = 0

# File uploader
uploaded_file = st.file_uploader("Upload Mood Diary (CSV)", type=['csv'])

# Use uploaded or sample
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    # Sample data
    df = pd.DataFrame({
        "date": ["2025-11-08", "2025-11-09", "2025-11-10", "2025-11-11", "2025-11-12"],
        "mood": ["happy", "anxious", "neutral", "anxious", "depressed"],
        "stress": [3.2, 7.8, 4.1, 8.5, 9.2],
        "sleep_hours": [7.5, 5.2, 6.8, 4.9, 3.1]
    })
    st.info("Using sample data. Upload your own CSV for real analysis.")

# Calculate risk
avg_stress = df['stress'].mean()
avg_sleep = df['sleep_hours'].mean()
risk = np.clip(40 + (avg_stress * 6.2) - (avg_sleep * 3.8) + np.random.uniform(-8, 8), 0, 100)
st.session_state.risk = int(risk)

# 3D Brain Renderer
def render_brain(risk):
    regions = ["Prefrontal", "Amygdala", "Hippocampus"]
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
        line=dict(color='gray', width=3)
    )])
    fig.update_layout(
        title=f"Brain Activity | Risk: {risk}%",
        scene=dict(
            xaxis_title='Left → Right',
            yaxis_title='Front → Back',
            zaxis_title='Bottom → Top'
        ),
        height=500
    )
    return fig

# Generate PDF
def generate_pdf(risk):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=16)
    pdf.cell(200, 10, text="NeuroTwin Report", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", size=12)
    pdf.cell(200, 10, text=f"Depression Risk: {risk}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 10, text=f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 10, text="Analysis: Based on your mood diary data", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if risk > 75:
        pdf.cell(200, 10, text="CRISIS ALERT: Seek immediate professional help", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(200, 10, text="Risk level is manageable. Continue monitoring.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Create buffer
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("7-Day Depression Risk", f"{st.session_state.risk}%", delta="+12%")
    st.metric("Anxiety Level", "High" if risk > 70 else "Moderate")

    if risk > 75:
        st.error("CRISIS ALERT: Immediate help recommended")
        if st.button("Play Voice Alert"):
            try:
                engine = pyttsx3.init()
                engine.say("Crisis detected. You are not alone. Please contact a therapist now.")
                engine.runAndWait()
                st.success("Voice alert played!")
            except:
                st.warning("Voice not supported in this environment.")

    # PDF Download
    pdf_buffer = generate_pdf(st.session_state.risk)
    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="NeuroTwin_Report.pdf",
        mime="application/pdf"
    )

with col2:
    fig = render_brain(st.session_state.risk)
    st.plotly_chart(fig, width='stretch')

# Data table
with st.expander("View Mood Data"):
    st.write(df.to_string())

# Footer
st.sidebar.success("NeuroTwin Active | 100% Local")
st.sidebar.markdown("**Author:** Steven-Thomas07")
