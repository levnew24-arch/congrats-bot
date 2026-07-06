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
        gender_instruction = f"Имя {name_capitalized} - ЖЕНСКОЕ. Используй ЖЕНСКИЙ РОД: дорогая, прекрасная, замечательная, талантливая, она, её, тебя, тебе."
        gender_examples = f"Пример правильного обращения: 'Дорогая {name_capitalized}! Ты прекрасная девушка!'"
    else:
        gender_instruction = f"Имя {name_capitalized} - МУЖСКОЕ. Используй МУЖСКОЙ РОД: дорогой, замечательный, талантливый, он, его, тебя, тебе."
        gender_examples = f"Пример правильного обращения: 'Дорогой {name_capitalized}! Ты замечательный парень!'"
    
    user_prompt = f"""Напиши поздравление с днём рождения.

Имя именинника: {name_capitalized}
Возраст: {age} лет
Увлечения: {hobby}
Стиль поздравления: {style}

{gender_instruction}
{gender_examples}

КРИТИЧЕСКИ ВАЖНО:
1. Имя {name_capitalized} пиши ТОЛЬКО с одной большой буквы в начале - НИКОГДА не пиши ВСЁ ИМЯ КАПСОМ ({name_capitalized.upper()} - запрещено)!
2. Пиши ОБЫЧНЫМ текстом - НЕ ПИШИ КАЖДОЕ СЛОВО С БОЛЬШОЙ БУКВЫ!
3. Начало КАЖДОГО предложения пиши с БОЛЬШОЙ буквы
4. Все остальные слова в предложении пиши СТРОЧНЫМИ (маленькими) буквами, кроме имён собственных!
5. Пиши ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! Абсолютно никаких английских слов!
6. Используй ТОЛЬКО имя {name_capitalized} - никогда не заменяй его на другое имя!
7. Весь текст должен быть в правильном грамматическом роде согласно имени {name_capitalized}
8. Используй правильную пунктуацию (точки, запятые, восклицательные знаки)
9. Никаких смешанных языков - только чистый русский!
10. Объём: 150-250 слов
11. Будь искренним и креативным, избегай банальных штампов

Примеры ПРАВИЛЬНОГО текста:
✅ "Дорогая Малика, с днём рождения! Она любит рыбалку, и это отлично!"
✅ "Дорогая Аня, ты прекрасная девушка! Мы тебя поздравляем!"

Примеры НЕПРАВИЛЬНОГО текста (НИКОГДА так не пиши):
❌ "Прекрасная МАЛИКА, С Днём Рождения!" (имя капсом)
❌ "Она Любит Рыбалку, И Это Отлично!" (каждое слово с большой)
❌ "ДОРОГАЯ МАЛИКА, МЫ ТЕБЯ ПОЗДРАВЛЯЕМ!" (весь текст капсом)

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
                    {"role": "system", "content": "Ты — креативный ведущий праздников. Пиши живые, искренние поздравления ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. Никогда не используй английские слова. Всегда определяй пол по имени и используй правильный грамматический род. Имя именинника ВСЕГДА пиши с одной большой буквы (НЕ КАПСОМ). Пиши обычным текстом - НЕ ПИШИ КАЖДОЕ СЛОВО С БОЛЬШОЙ БУКВЫ. Начало каждого предложения — с большой буквы, остальные слова строчными. Используй правильную пунктуацию."},
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
