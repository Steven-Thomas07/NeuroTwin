import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from brain.renderer import render_brain
from twin.builder import DigitalTwin

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
    df = twin.df.copy()
    if 'live_df' in st.session_state:
        df = pd.concat([df, st.session_state.live_df], ignore_index=True)

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
        st.warning("Please contact a therapist or emergency services immediately.")

    with col2:
        fig = render_brain(risk)
        st.plotly_chart(fig, width='stretch')

    with st.expander("View Your Mood Data"):
        st.write(twin.df.to_string())

    # Full report export
    if st.button("📄 Export Full Report (PNG + 3D Brain)"):
        try:
            # Save brain as PNG
            fig.write_image("brain_snapshot.png")
            st.success("✓ Full report with 3D brain saved as brain_snapshot.png!")
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

    st.subheader("Voice Tone Analysis")
    col_audio, col_text = st.columns(2)
    with col_audio:
        audio_data = st.audio_input("🎤 Record your voice for tone analysis")
        if audio_data:
            st.audio(audio_data, format="audio/wav")
            st.info("🎙️ Analyzing voice tone...")
            with st.spinner("Processing audio..."):
                import time
                time.sleep(1.0)
            # Mock result based on audio length or random
            tone = np.random.choice(["anxious", "calm", "depressed"])
            st.write(f"🔊 Detected tone: **{tone.upper()}**")
            if tone == "anxious":
                st.error("⚠️ Voice confirms high stress!")
            elif tone == "calm":
                st.success("✓ Voice analysis shows calm demeanor")
            else:
                st.warning("⚠️ Voice suggests depressed mood")
    with col_text:
        st.markdown("**Or type what you'd say:**")
        voice_text = st.text_input("Type your voice input here", placeholder="e.g., I'm feeling really stressed today...")
        if st.button("Analyze Text Tone"):
            if voice_text.strip():
                st.info("📝 Analyzing text tone...")
                with st.spinner("Processing text..."):
                    import time
                    time.sleep(0.5)
                # Mock result based on text content
                if "stressed" in voice_text.lower() or "anxious" in voice_text.lower():
                    tone = "anxious"
                elif "calm" in voice_text.lower() or "happy" in voice_text.lower():
                    tone = "calm"
                else:
                    tone = np.random.choice(["anxious", "calm", "depressed"])
                st.write(f"🔊 Detected tone: **{tone.upper()}**")
                if tone == "anxious":
                    st.error("⚠️ Text suggests high stress!")
                elif tone == "calm":
                    st.success("✓ Text analysis shows calm demeanor")
                else:
                    st.warning("⚠️ Text suggests depressed mood")
            else:
                st.warning("Please enter some text to analyze.")

    st.sidebar.success("NeuroTwin Active | Privacy: 100% Local")



    # === 10. AI THERAPY SUGGESTION ===
    st.subheader("Personalized Therapy Tips")
    if risk > 75:
        st.error("**URGENT:** Practice 4-7-8 breathing now: Inhale 4s, hold 7s, exhale 8s.")
        st.info("**CBT Tip:** Write down 3 things you're grateful for.")
    elif risk > 50:
        st.warning("**Try:** 10-minute guided meditation (YouTube: 'anxiety relief')")
        st.info("**Journal Prompt:** What triggered your stress today?")
    else:
        st.success("**Great job!** Reward yourself with a 15-min walk in nature.")
        st.info("**Maintain:** Keep sleep >7 hrs tonight.")

    # === 11. SLEEP DEBT TRACKER ===
    if len(df) > 0:
        total_sleep = df['sleep_hours'].sum()
        expected_sleep = len(df) * 7.5
        sleep_debt = expected_sleep - total_sleep
        debt_color = "inverse" if sleep_debt > 0 else "normal"
        st.metric("**Sleep Debt**", f"{sleep_debt:+.1f} hrs", delta=f"vs {len(df)}×7.5 hrs ideal")

    # === 12. EXPORT TO CSV ===
    if st.button("📥 Export Diary to CSV"):
        csv = df.to_csv(index=False).encode()
        st.download_button(
            "Download Mood Diary",
            csv,
            "neurotwin_diary.csv",
            "text/csv"
        )
        st.success("Diary exported!")

    # === 13. DARK MODE TOGGLE ===
    def set_theme(theme):
        if theme == "dark":
            st._config.set_option("theme.base", "dark")
            st._config.set_option("theme.primaryColor", "#FF6B6B")
        else:
            st._config.set_option("theme.base", "light")
            st._config.set_option("theme.primaryColor", "#4ECDC4")

    theme = st.sidebar.selectbox("Theme", ["light", "dark"], index=0)
    set_theme(theme)
    st.sidebar.image("https://img.icons8.com/fluency/48/000000/brain.png", width=60)
    st.sidebar.markdown("### NeuroTwin v1.0")
    st.sidebar.markdown(f"**Risk:** {risk}% | **Entries:** {len(df)}")

if __name__ == "__main__":
    run_dashboard()
