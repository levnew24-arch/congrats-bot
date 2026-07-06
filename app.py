from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GROQ_KEY = "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"
MODEL = "llama-3.3-70b-versatile"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    hobby = data.get('hobby')
    style = data.get('style')
    
    # Капитализируем имя (только первая буква большая)
    name_capitalized = name.capitalize() if name else name
    
    # Определяем пол по окончанию имени
    female_endings = ['а', 'я', 'ия', 'ея']
    is_female = any(name.lower().rstrip('ь').endswith(end) for end in female_endings)
    
    if is_female:
        gender_pronoun = "ей"  # Ей уже 12 лет
        gender_address = "ты, тебе, твой, твоя, твоё"  # Обращение на ты
        gender_adj = "дорогая, прекрасная, замечательная"
        gender_instruction = f"Имя {name_capitalized} - ЖЕНСКОЕ. Используй: {gender_adj}, {gender_address}."
    else:
        gender_pronoun = "ему"  # Ему уже 12 лет
        gender_address = "ты, тебе, твой, твоя, твоё"
        gender_adj = "дорогой, замечательный, прекрасный"
        gender_instruction = f"Имя {name_capitalized} - МУЖСКОЕ. Используй: {gender_adj}, {gender_address}."
    
    user_prompt = f"""Напиши поздравление с днём рождения.

Имя именинника: {name_capitalized}
Возраст: исполняется {age} лет
Увлечения: {hobby}
Стиль поздравления: {style}

{gender_instruction}

КРИТИЧЕСКИ ВАЖНО ДЛЯ РУССКОГО ЯЗЫКА:
1. Обращайся к имениннику НАПРЯМУЮ на "ты" ({gender_address}). Используй "поздравляем тебя", "ты замечательная", "желаем тебе".
2. НИКОГДА не переключайся на третье лицо ("она", "её", "он", "его") в середине текста! Весь текст должен быть обращением к "ты".
3. Возраст пиши как "Ей уже {age} лет" или "Ему уже {age} лет" (НЕ "Она уже {age} лет"!).
4. Имя {name_capitalized} пиши ТОЛЬКО с одной большой буквы - НИКОГДА не пиши ВСЁ ИМЯ КАПСОМ!
5. Пиши ОБЫЧНЫМ текстом - НЕ ПИШИ КАЖДОЕ СЛОВО С БОЛЬШОЙ БУКВЫ!
6. Начало КАЖДОГО предложения пиши с БОЛЬШОЙ буквы
7. Все остальные слова в предложении пиши СТРОЧНЫМИ (маленькими) буквами, кроме имён собственных!
8. Пиши ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! Абсолютно никаких английских слов!
9. Используй ТОЛЬКО имя {name_capitalized} - никогда не заменяй его на другое имя!
10. Используй правильную пунктуацию (точки, запятые, восклицательные знаки)
11. Объём: 150-250 слов
12. Будь искренним и креативным, избегай банальных штампов

Пример ПРАВИЛЬНОГО текста:
✅ "Дорогая Малика, поздравляем тебя с днём рождения! Ей уже 12 лет. Ты прекрасная девушка, которая любит рыбалку. Мы желаем тебе..."

Примеры НЕПРАВИЛЬНОГО текста (НИКОГДА так не пиши):
❌ "Прекрасная МАЛИКА, С Днём Рождения!" (имя капсом)
❌ "Она Любит Рыбалку, И Это Отлично!" (каждое слово с большой)
❌ "Дорогая Малика... Она уже 12 лет... Она любит рыбалку... Мы её любим..." (нельзя использовать "она/её", только "ты/тебе"!)
❌ "Она уже 12 лет" (неправильно! Правильно: "Ей уже 12 лет")

Напиши поздравление на русском языке."""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "Ты — креативный ведущий праздников. Пиши живые, искренние поздравления ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. Никогда не используй английские слова. Имя именинника ВСЕГДА пиши с одной большой буквы (НЕ КАПСОМ). Пиши обычным текстом - НЕ ПИШИ КАЖДОЕ СЛОВО С БОЛЬШОЙ БУКВЫ. Обращайся к имениннику напрямую на 'ты' (тебя, тебе, твой). НИКОГДА не переключайся на третье лицо ('она', 'её', 'он', 'его'). Возраст пиши как 'Ей уже X лет' или 'Ему уже X лет' (НЕ 'Она уже X лет'!). Начало каждого предложения — с большой буквы, остальные слова строчными. Используй правильную пунктуацию."},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.8
            },
            timeout=30
        )
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            text = result["choices"][0]["message"]["content"]
            return jsonify({"success": True, "text": text})
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error")
            return jsonify({"success": False, "error": error_msg}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
