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

def make_response(text, end=False):
    """Собираем ответ для Алисы в правильном формате"""
    if len(text) > 900:
        text = text[:900]
    return {
        "response": {
            "text": text,
            "tts": text,
            "end_session": end
        },
        "version": "1.0"
    }

@app.post("/alice")
async def alice(request: Request):
    data = await request.json()
    user_text = data.get("request", {}).get("command", "").strip()

    # Если Алиса просто проверяет связь или пользователь молчит
    if not user_text:
        return make_response("Привет! Спроси меня о чём-нибудь.")

    # Если пользователь просит выйти
    if user_text.lower() in ["выход", "стоп", "хватит", "пока"]:
        return make_response("Пока! Обращайся ещё.", end=True)

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
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Ошибка Groq:", e)
        answer = "Прости, у меня что-то сломалось. Попробуй ещё раз."

    return make_response(answer)
