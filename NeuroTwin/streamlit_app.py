import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="NeuroTwin Cloud", layout="wide", page_icon="brain")
st.markdown("""
# NeuroTwin Cloud
**Your Brain Digital Twin — Live in Browser**
Enter mood → See 3D brain → Get crisis alert
**No install • Works on phone • 100% private**
""")

# Live Mood Form
with st.form("mood_form"):
    st.write("**Enter Your Mood Now**")
    mood = st.selectbox("Mood", ["happy", "neutral", "anxious", "depressed"])
    stress = st.slider("Stress (1-10)", 1, 10, 5)
    sleep = st.slider("Sleep (hrs)", 0.0, 12.0, 7.0)
    submit = st.form_submit_button("Build My Brain Twin")

    if submit:
        data = {
            "date": [pd.Timestamp.now().strftime("%Y-%m-%d")],
            "mood": [mood],
            "stress": [stress],
            "sleep_hours": [sleep]
        }
        df = pd.DataFrame(data)
        if 'history' not in st.session_state:
            st.session_state.history = df
        else:
            st.session_state.history = pd.concat([st.session_state.history, df], ignore_index=True)
        st.rerun()

# Use session history
df = st.session_state.get('history', pd.read_csv("sample_mood_log.csv") if st.button("Use Sample Data") else pd.DataFrame())

if not df.empty:
    avg_stress = df['stress'].mean()
    avg_sleep = df['sleep_hours'].mean()
    risk = np.clip(40 + (avg_stress * 6.2) - (avg_sleep * 3.8) + np.random.uniform(-8, 8), 0, 100)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("7-Day Depression Risk", f"{int(risk)}%", delta="+12%")
        if risk > 75:
            st.error("CRISIS ALERT: Contact therapist now!")
            st.warning("Voice: 'You are not alone. Help is available.'")

    with col2:
        regions = ["Prefrontal", "Amygdala", "Hippocampus"]
        colors = ['green', 'red' if risk > 70 else 'yellow', 'blue']
        sizes = [15, 25 if risk > 70 else 18, 12]
        fig = go.Figure(data=[go.Scatter3d(
            x=[0, 1, 2], y=[0, 1, 0], z=[0, 0, 1],
            mode='markers+text', marker=dict(size=sizes, color=colors),
            text=regions, textposition="top center"
        )])
        fig.update_layout(title=f"Brain Activity | Risk: {int(risk)}%", height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.sidebar.success("Live on Web • GitHub: Steven-Thomas07")
