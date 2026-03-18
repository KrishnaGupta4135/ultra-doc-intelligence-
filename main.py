import subprocess
import sys

def run_fastapi():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"]
    )

def run_streamlit():
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"]
    )

if __name__ == "__main__":
    print("Starting FastAPI + Streamlit...")

    fastapi_process = run_fastapi()
    streamlit_process = run_streamlit()

    try:
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("Stopping all services...")
        fastapi_process.terminate()
        streamlit_process.terminate()