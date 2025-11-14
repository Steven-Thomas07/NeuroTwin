# NeuroTwin: AI Brain Digital Twin for Mental Health

NeuroTwin is a small demo dashboard that accepts mood diary CSVs, live mood entries, and voice input to visualize a 3D brain and provide risk recommendations.

Features
- CSV / Live Mood Upload → Real-Time Risk Prediction
- 3D Interactive Brain Visualization (Plotly)
- Voice Sentiment Analysis (Web Speech API, mock detection)
- Crisis Alerts & PDF Reports

Run locally
1. Create and activate virtualenv
   ```powershell
   cd "C:\Users\Steven S\Desktop\final1"
   & "C:/Users/Steven S/Desktop/final1/.venv/Scripts/Activate.ps1"
   ```
2. Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```
3. Start the app
   ```powershell
   python -m streamlit run app.py --server.port 8501
   ```

Deploy to Streamlit Cloud
1. Create a GitHub repo (e.g., `Steven-Thomas07/NeuroTwin`) and push these files.
2. Go to https://share.streamlit.io and create a new app pointing to `app.py` on the `main` branch.

Notes
- If Streamlit asks for an onboarding email in the terminal, press Enter to skip it so the server will finish booting.
- `kaleido` is required for saving Plotly images used in the PDF export.

Author: Steven Thomas
