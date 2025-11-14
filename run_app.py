#!/usr/bin/env python
"""
Launch NeuroTwin dashboard without interactive prompts
"""
import subprocess
import os
import sys

os.chdir(r"C:\Users\Steven S\Desktop\final1\NeuroTwin")

# Kill any existing Streamlit processes
os.system("taskkill /f /im streamlit.exe 2>nul")

# Set environment variables to skip email prompt
os.environ['STREAMLIT_BROWSER_GATHERUSAGESTATS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'false'

# Launch Streamlit
cmd = [
    sys.executable, "-m", "streamlit", "run", 
    "dashboard/app.py",
    "--server.runOnSave=false",
    "--logger.level=warning"
]

print("=" * 60)
print("Starting NeuroTwin Dashboard")
print("=" * 60)
print("\n✓ Opening at http://localhost:8501")
print("\nFeatures available:")
print("  • Live Mood Form")
print("  • Trend Chart")
print("  • Therapy Recommendations")
print("  • PDF Export")
print("  • Voice Analysis")
print("  • CSV Upload")
print("\n" + "=" * 60 + "\n")

subprocess.run(cmd)
