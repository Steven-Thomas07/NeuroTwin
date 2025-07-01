import streamlit as st
import pyttsx3
import pandas as pd
from brain.renderer import render_brain
from twin.builder import DigitalTwin
import os

def run_dashboard(twin=None):
    st.set_page_config(page_title="NeuroTwin", layout="wide", page_icon="brain")
    st.markdown("# NeuroTwin: Your Personal Brain Digital Twin")
    st.markdown("**Upload your mood diary → See your brain in 3D → Get crisis alerts**")

    uploaded = st.file_uploader("Upload Mood Diary (CSV)", type=['csv'])
    
    if uploaded:
        path = f"data/uploaded_{uploaded.name}"
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        twin = DigitalTwin(path)
    elif twin is None:
        twin = DigitalTwin("data/sample_mood_log.csv")
        st.info("Using sample data. Upload your own for personalized twin.")

    if 'twin' not in st.session_state:
        twin.build()
        st.session_state.twin = twin

    twin = st.session_state.twin
    risk = twin.predict_depression()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("7-Day Depression Risk", f"{risk}%", delta="+12%")
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
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Your Mood Data"):
        st.dataframe(twin.df)

    if st.button("Export Report"):
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Depression Risk: {risk}%", ln=1)
        pdf.cell(200, 10, txt=f"Anxiety Level: {'High' if risk > 70 else 'Moderate'}", ln=1)
        pdf.cell(200, 10, txt="NeuroTwin Report Generated", ln=1)
        pdf.output("NeuroTwin_Report.pdf")
        st.success("Report exported as NeuroTwin_Report.pdf")

    st.sidebar.success("NeuroTwin Active | Privacy: 100% Local")
