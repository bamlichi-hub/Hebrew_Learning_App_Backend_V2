import os
import shutil
from datetime import datetime
from fastapi import FastAPI, Response, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # אופציונלי: אם תרצה לגשת לקבצים מהדפדפן
from gtts import gTTS
import io
import uvicorn

app = FastAPI()

# --- הגדרות CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- הגדרת תיקיית שמירה להקלטות ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# אופציונלי: מאפשר גישה לקבצים דרך URL (למשל: http://localhost:8000/uploads/filename.webm)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- Endpoints ---

@app.get("/")
def home():
    return {"message": "Hadari Server is Speaking & Listening! 🗣️👂"}

# 1. יצירת דיבור (קיים)
@app.get("/tts")
def tts(text: str):
    print(f"Generating audio for: {text}")
    
    # שימוש ב-iw לעברית (תקן ישן שגוגל לעיתים מעדיפים)
    tts = gTTS(text=text, lang='iw')
    
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    
    return Response(content=audio_data.read(), media_type="audio/mpeg")

# 2. קבלת הקלטה (חדש!)
@app.post("/api/upload-audio")
async def upload_audio(
    audio: UploadFile = File(...),
    letter: str = Form(...),
    user: str = Form(...)
):
    try:
        # יצירת שם קובץ ייחודי: user_letter_timestamp.webm
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{user}_{letter}_{timestamp}.webm"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # שמירת הקובץ פיזית בשרת
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        print(f"🎤 Audio saved successfully: {safe_filename}")
        
        # החזרת תשובה ללקוח
        return {
            "status": "success", 
            "filename": safe_filename,
            "path": file_path
        }
        
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # שים לב: הפורט הוא 8000. וודא שב-React ב-useAudioRecorder הכתובת היא localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
