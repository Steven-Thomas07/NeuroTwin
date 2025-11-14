"""
Root shim to run the NeuroTwin Streamlit app located under NeuroTwin/dashboard.
This file keeps the repo layout compatible with Streamlit Cloud (expects an app.py at root).
"""
import runpy
import os

app_path = os.path.join(os.path.dirname(__file__), "NeuroTwin", "dashboard", "app_run.py")
if not os.path.exists(app_path):
    # fall back to the original app if present
    app_path = os.path.join(os.path.dirname(__file__), "NeuroTwin", "dashboard", "app.py")

if not os.path.exists(app_path):
    raise FileNotFoundError(f"Could not find NeuroTwin dashboard app at {app_path}")

# Execute the Streamlit app script
runpy.run_path(app_path, run_name="__main__")
