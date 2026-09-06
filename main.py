import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-c132e498cfb8429caeecac1dce377562")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class VoiceRequest(BaseModel):
    command: str

@app.post("/api/voice")
async def handle_voice_query(req: VoiceRequest):
    # Проверяем ключевую фразу на сервере
    if "привет стасик" not in req.command.lower():
        return {"status": "ignored", "response": "Фактическая команда не распознана"}

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент по имени Стасик. Отвечай кратко и с юмором."},
            {"role": "user", "content": "Пользователь позвал тебя: " + req.command}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        res_data = response.json()
        answer = res_data["choices"][0]["message"]["content"]
        return {"status": "success", "response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
