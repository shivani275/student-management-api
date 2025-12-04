import subprocess
import time
import requests
import sys
import signal

def wait_for_api(url="http://127.0.0.1:8000", timeout=15):
    """
    Wait for FastAPI server to start.
    """
    start = time.time()
    while True:
        try:
            r = requests.get(url)
            if r.status_code in [200, 404]:
                print("API is ready!")
                break
        except requests.exceptions.RequestException:
            pass

        if time.time() - start > timeout:
            print("API did not start in time. Continuing anyway...")
            break

        time.sleep(0.5)

# -----------------------------------------------------
# Start Uvicorn (FastAPI backend)
# -----------------------------------------------------
api_process = subprocess.Popen(
    ["uvicorn", "main:app", "--reload", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

wait_for_api()

# -----------------------------------------------------
# Start Streamlit dashboard
# -----------------------------------------------------
streamlit_process = subprocess.Popen(
    ["streamlit", "run", "dashboard.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

try:
    # Wait for both processes (non-blocking)
    while True:
        if api_process.poll() is not None or streamlit_process.poll() is not None:
            break
        time.sleep(1)
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Terminating processes...")
finally:
    for proc in [api_process, streamlit_process]:
        try:
            proc.send_signal(signal.SIGINT)
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass
    print("Both FastAPI and Streamlit processes terminated.")
