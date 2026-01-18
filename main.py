from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import io
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hadari Server is Speaking! 🗣️"}

@app.get("/tts")
def tts(text: str):
    print(f"Generating audio for: {text}")
    
    # התיקון כאן: שינוי he ל-iw
    tts = gTTS(text=text, lang='iw')
    
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    
    return Response(content=audio_data.read(), media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)