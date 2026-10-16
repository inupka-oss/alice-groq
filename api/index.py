import os
from fastapi import FastAPI, Request
from openai import OpenAI
from mangum import Mangum

groq_key = os.environ.get("GROQ_API_KEY")

if groq_key:
    client = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )
    MODEL = "openai/gpt-oss-20b"
else:
    client = None
    MODEL = None

app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "ok",
        "groq_configured": groq_key is not None
    }


@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "").strip()

    if client is None:
        return {
            "response": {"text": "Ключ Groq не настроен.", "end_session": False},
            "version": "1.0"
        }

    if not user_text:
        answer = "Привет! Спроси меня о чём угодно."
    else:
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Ты мой друг. Отвечай кратко, максимум 3 предложения."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=200
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            print("Ошибка Groq:", e)
            answer = f"Ошибка: {str(e)[:200]}"

    if len(answer) > 900:
        answer = answer[:900]

    return {
        "response": {"text": answer, "end_session": False},
        "version": "1.0"
    }


handler = Mangum(app)
