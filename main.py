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

@app.head("/")
def head():
    return {}

def make_response(text, end=False):
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
    session = data.get("session", {})
    user_text = data.get("request", {}).get("command", "").strip()
    is_new = session.get("new", False)

    # Если Алиса только запустила навык — здороваемся
    if is_new and not user_text:
        return make_response("Привет! Я умный бот. Спроси меня о чём угодно.")

    # Если команда пустая — просим повторить
    if not user_text:
        return make_response("Я не расслышала. Повтори, пожалуйста.")

    # Выход
    if user_text.lower() in ["выход", "стоп", "хватит", "пока", "до свидания"]:
        return make_response("Пока! Обращайся ещё.", end=True)

    # Отправляем в Groq
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # быстрая модель для скорости
            messages=[
                {"role": "system", "content": "Ты дружелюбный ассистент. Отвечай кратко, максимум 3 предложения."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=250
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Ошибка Groq:", e)
        answer = "Прости, у меня что-то сломалось. Попробуй ещё раз."

    return make_response(answer)
