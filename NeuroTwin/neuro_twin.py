import os
from twin.builder import DigitalTwin
from dashboard.app import run_dashboard

print("NeuroTwin: Building Your Brain Digital Twin...")
twin = DigitalTwin("NeuroTwin/data/sample_mood_log.csv")
twin.build()
risk = twin.predict_depression()
print(f"7-Day Depression Risk: {risk}%")
print("Launching 3D Brain Dashboard...")
run_dashboard(twin)
