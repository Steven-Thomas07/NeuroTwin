#!/usr/bin/env python
"""
Launch NeuroTwin Dashboard without interactive prompts
"""
import subprocess
import sys
import os

os.chdir(r"C:\Users\Steven S\Desktop\final1\NeuroTwin")
sys.path.insert(0, ".")

# Set environment to skip prompts
os.environ["STREAMLIT_CLIENT_GATHERUSAGESTATS"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"

# Run streamlit with stdin closed to skip email prompt
try:
    # Use stdin=subprocess.DEVNULL to prevent blocking on input
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    print("=" * 60)
    print("✓ NeuroTwin Dashboard Starting...")
    print("=" * 60)
    print("\nURL: http://localhost:8501")
    print("\nFeatures:")
    print("  ✓ Live Mood Form")
    print("  ✓ Trend Chart")
    print("  ✓ Therapy Recommendations")
    print("  ✓ PDF Export")
    print("  ✓ Voice Analysis")
    print("  ✓ CSV Upload")
    print("\n" + "=" * 60)
    
    # Keep process running
    process.wait()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
