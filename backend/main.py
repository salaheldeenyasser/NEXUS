import sys
import os
sys.path.append("/home/salah/doorLockGui")  # Ensure deepface_scripts is importable
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import admin, access, system_settings, user_profiles, gui_utils
import webview
import uvicorn
from threading import Thread

# FastAPI setup
app = FastAPI(
    title="RP5 Access Control API",
    description="Handles multi-factor authentication via pin, fingerprint, and face recognition.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok"}

app.include_router(admin.router, prefix="/admin")
app.include_router(access.router, prefix="/access")
app.include_router(system_settings.router, prefix="/settings")
app.include_router(user_profiles.router, prefix="/users")
app.include_router(gui_utils.router, prefix="/gui", tags=["gui"])

# Function to run FastAPI
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start FastAPI and PyWebView together
if __name__ == "__main__":
    # Run FastAPI in a separate thread
    thread = Thread(target=run_fastapi)
    thread.start()
    webview.create_window(
        'Smart Lock',
        'http://localhost:3000/',
        js_api=app,
        fullscreen=True,
        frameless=True,
        width=240,
        height=320,
        resizable=False
    )
    webview.start()