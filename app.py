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
    
    # Определяем пол по окончанию имени
    female_endings = ['а', 'я', 'ия', 'ея']
    is_female = any(name.lower().rstrip('ь').endswith(end) for end in female_endings)
    
    if is_female:
        gender_instruction = f"Имя {name} - ЖЕНСКОЕ. Используй ЖЕНСКИЙ РОД: дорогая, прекрасная, замечательная, талантливая, она, её, тебя, тебе."
        gender_examples = f"Пример правильного обращения: 'Дорогая {name}! Ты прекрасная девушка!'"
    else:
        gender_instruction = f"Имя {name} - МУЖСКОЕ. Используй МУЖСКОЙ РОД: дорогой, замечательный, талантливый, он, его, тебя, тебе."
        gender_examples = f"Пример правильного обращения: 'Дорогой {name}! Ты замечательный парень!'"
    
    user_prompt = f"""Напиши поздравление с днём рождения.

Имя именинника: {name}
Возраст: {age} лет
Увлечения: {hobby}
Стиль поздравления: {style}

{gender_instruction}
{gender_examples}

СТРОГИЕ ПРАВИЛА (обязательны к выполнению):
1. Пиши ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! Абсолютно никаких английских слов!
2. Используй ТОЛЬКО имя {name} - никогда не заменяй его на другое имя (никаких "Андрей", "Иван" и т.д.)!
3. Весь текст должен быть в правильном грамматическом роде согласно имени {name}
4. Никаких смешанных языков - только чистый русский!
5. Объём: 150-250 слов
6. Будь искренним и креативным, избегай банальных штампов

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
                    {"role": "system", "content": "Ты — креативный ведущий праздников. Пиши живые, искренние поздравления ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. Никогда не используй английские слова. Всегда определяй пол по имени и используй правильный грамматический род. Используй ТОЛЬКО то имя, которое указал пользователь."},
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
