from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Predefined non-therapeutic responses
EDUCATIONAL_RESPONSES = {
    "stress": "Справувањето со стресот може да вклучува техники на длабоко дишење, редовно вежбање, одржување на здрава исхрана и доволно сон. Може да пробате и техники на внимателност (mindfulness) или медитација.",
    "loneliness": "Чувството на осаменост е нормално. Можете да пробате да се поврзете со пријатели или семејство, да се вклучите во групни активности или волонтерски работи. Онлајн заедниците исто така можат да бидат корисни.",
    "anxiety": "За анксиозноста, може да пробате техники на заземеност (grounding), како броење предмети околу вас или фокусирање на дишењето. Редовната физичка активност и ограничување на кофеинот можат да помогнат.",
    "default": "Ова е едукативен чатбот за општи прашања поврзани со менталното здравје. Можете да прашате за стрес, осаменост, анксиозност или слични теми. Забелешка: Ова не е замена за професионална психолошка помош."
}

def get_chatbot_response(user_input):
    user_input = user_input.lower()
    
    # Check for keywords
    if "стрес" in user_input:
        return EDUCATIONAL_RESPONSES["stress"]
    elif "осамен" in user_input or "осамено" in user_input:
        return EDUCATIONAL_RESPONSES["loneliness"]
    elif "анксиоз" in user_input:
        return EDUCATIONAL_RESPONSES["anxiety"]
    else:
        # If no keyword matches, use OpenAI API or default response
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Вие сте едукативен чатбот за ментално здравје. Давајте кратки, општи совети. Нагласете дека ова не е професионален совет. Одговорите треба да бидат на македонски јазик."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return EDUCATIONAL_RESPONSES["default"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)