import os
from fastapi import FastAPI, Request
from openai import OpenAI
from mangum import Mangum

client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "").strip()

    if not user_text:
        answer = "Привет! Спроси меня о чём угодно."
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Ты дружелюбный ассистент. Отвечай кратко."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=200
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            print("Ошибка Groq:", e)
            answer = "Извини, я не смогла ответить."

    if len(answer) > 900:
        answer = answer[:900]

    return {
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": "1.0"
    }

handler = Mangum(app)
