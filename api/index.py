import os
from fastapi import FastAPI, Request
from openai import OpenAI
from mangum import Mangum

# Проверяем, есть ли ключ Gemini
gemini_key = os.environ.get("GEMINI_API_KEY")

if gemini_key:
    client = OpenAI(
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    MODEL = "gemini-3.5-flash"
else:
    client = None
    MODEL = None

app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "ok",
        "gemini_configured": gemini_key is not None
    }


@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "").strip()

    if client is None:
        return {
            "response": {
                "text": "Ключ Gemini не настроен.",
                "end_session": False
            },
            "version": "1.0"
        }

    if not user_text:
        answer = "Привет! Спроси меня о чём угодно."
    else:
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Ты мой друг. Отвечай с юмороми матом"},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=800
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            print("Ошибка Gemini:", e)
            answer = f"Ошибка: {str(e)[:200]}"

    if len(answer) > 1000:
        answer = answer[:1000]

    return {
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": "1.0"
    }


handler = Mangum(app)
