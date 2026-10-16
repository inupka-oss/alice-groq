import os
from fastapi import FastAPI, Request
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "")

    if not user_text:
        return {
            "response": {
                "text": "Я тебя не расслышала, повтори.",
                "tts": "Я тебя не расслышала, повтори.",
                "end_session": False
            },
            "version": "1.0"
        }

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты дружелюбный ассистент. Отвечай кратко, максимум 3 предложения."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=300
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        print("Ошибка:", e)
        answer = "Прости, у меня что-то сломалось. Попробуй позже."

    if len(answer) > 1000:
        answer = answer[:1000]

    return {
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": False
        },
        "version": "1.0"
    }
