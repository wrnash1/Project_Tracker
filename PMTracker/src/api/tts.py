from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
import tempfile
from pathlib import Path

router = APIRouter()

@router.post("/speak")
async def text_to_speech(text: str, language: str = 'en'):
    """Convert text to speech and return audio file"""
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_path = temp_file.name
        temp_file.close()

        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(temp_path)

        return FileResponse(
            temp_path,
            media_type='audio/mpeg',
            filename='speech.mp3'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for TTS"""
    return {
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'es', 'name': 'Spanish'},
            {'code': 'fr', 'name': 'French'},
            {'code': 'de', 'name': 'German'},
            {'code': 'it', 'name': 'Italian'},
            {'code': 'pt', 'name': 'Portuguese'},
            {'code': 'zh-CN', 'name': 'Chinese (Simplified)'},
            {'code': 'ja', 'name': 'Japanese'},
            {'code': 'ko', 'name': 'Korean'}
        ]
    }
