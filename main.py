import os
import speech_recognition as sr
from fastapi import FastAPI, HTTPException, UploadFile, File
import requests

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-c132e498cfb8429caeecac1dce377562")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.post("/api/voice")
async def handle_voice_query(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    recognizer = sr.Recognizer()
    try:
        # Указываем 8000 Гц в соответствии с настройками ESP32
        audio_data = sr.AudioData(audio_bytes, 8000, 2)
        text_command = recognizer.recognize_google(audio_data, language="ru-RU")
    except Exception as e:
        return {"status": "ignored", "response": f"Речь не распознана: {str(e)}"}

    if "привет стасик" not in text_command.lower():
        return {"status": "ignored", "response": f"Распознано, но нет ключа: {text_command}"}

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент по имени Стасик. Отвечай кратко и с юмором."},
            {"role": "user", "content": f"Пользователь сказал: {text_command}"}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        res_data = response.json()
        answer = res_data["choices"][0]["message"]["content"]
        return {"status": "success", "response": answer, "recognized": text_command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/question")
async def handle_question(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    recognizer = sr.Recognizer()
    try:
        # Здесь также меняем на 8000 Гц
        audio_data = sr.AudioData(audio_bytes, 8000, 2)
        text_command = recognizer.recognize_google(audio_data, language="ru-RU")
    except Exception as e:
        return {"status": "error", "response": "Не удалось расслышать вопрос"}

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент по имени Стасик. Отвечай кратко и с юмором."},
            {"role": "user", "content": text_command}
        ],
        "max_tokens": 200
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        res_data = response.json()
        answer = res_data["choices"][0]["message"]["content"]
        return {"status": "success", "response": answer, "recognized": text_command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
