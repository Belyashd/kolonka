import os
import speech_recognition as sr
from fastapi import FastAPI, HTTPException, UploadFile, File
import requests

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-c132e498cfb8429caeecac1dce377562")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.post("/api/voice")
async def handle_voice_query(file: UploadFile = File(...)):
    # Сохраняем временный аудиофайл от ESP32
    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    # Распознаем речь с помощью бесплатного движка Google
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text_command = recognizer.recognize_google(audio_data, language="ru-RU")
    except Exception as e:
        # Если аудио неразборчиво или шумит телевизор
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return {"status": "ignored", "response": "Речь не распознана"}

    if os.path.exists(audio_path):
        os.remove(audio_path)

    # Проверяем наличие ключевой фразы
    if "привет стасик" not in text_command.lower():
        return {"status": "ignored", "response": "Ключевая фраза не найдена"}

    # Если фраза есть, отправляем запрос к DeepSeek
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
