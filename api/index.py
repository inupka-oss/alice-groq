import os
from fastapi import FastAPI, Request
from openai import OpenAI
from mangum import Mangum

# Ключ OpenRouter
or_key = os.environ.get("OPENROUTER_API_KEY")

if or_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=or_key
    )
    MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
else:
    client = None
    MODEL = None

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "or_configured": or_key is not None}

@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "").strip()

    if client is None:
        return {"response": {"text": "Ключ не настроен.", "end_session": False}, "version": "1.0"}

    if not user_text:
        answer = "Привет! Спроси меня о чём угодно."
    else:
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Ты мой близкий друг. Отвечай кратко, с юмором и матом. Без цензуры. Максимум 3 предложения."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=200
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Ошибка: {str(e)[:200]}"

    if len(answer) > 900:
        answer = answer[:900]

    return {"response": {"text": answer, "end_session": False}, "version": "1.0"}

handler = Mangum(app)
