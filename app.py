from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

import os
GROQ_KEY = os.environ.get("GROQ_KEY", "")
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
    
    user_prompt = f"Напиши поздравление для {name}, которому исполняется {age} лет. Увлечения: {hobby}. Стиль: {style}. Пиши на русском языке, 150-250 слов, искренне и креативно, без штампов."
    
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
                    {"role": "system", "content": "Ты — креативный ведущий праздников. Пиши живые, искренние поздравления на русском языке."},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.8
            },
            timeout=30
        )
        
        print(f"Groq Status: {response.status_code}")
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            text = result["choices"][0]["message"]["content"]
            return jsonify({"success": True, "text": text})
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error")
            print(f"Error: {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 500
            
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
