from flask import Flask, render_template, request, jsonify
import openai
import os
import traceback

app = Flask(__name__)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY
print("API Key Loaded:", bool(OPENAI_KEY))




LOCAL_EDUCATIONAL_DB = {
    "стрес": {
        "base": "За стресот: Длабоко дишење, редовно вежбање, здрава исхрана и доволно сон се клучни. Техники на внимателност (mindfulness) и медитација се исто така корисни.",
        "techniques": """Конкретни техники за стрес:
1. 5-5-5 дишење: Вдишете 5 сек, држете 5 сек, издишете 5 сек.
2. Прогресивна релаксација на мускулите.
3. Водечки медитации од YouTube."""
    },
        "внимателност": {
        "base": "Техниките на внимателност (mindfulness) помагаат да си свесен за моментот и да го намалиш стресот.",
        "techniques": """Основни техники на внимателност:
1. Свесно дишење — фокусирај се само на дишењето.
2. Скенинг на телото — забележи каде чувствуваш тензија.
3. Медитација на внимателност — седи мирно и набљудувај ги мислите без да судиш."""
    },
    "професионална помош": {
        "base": "Професионална помош можете да побарате кај лиценцирани психолози, психијатри или во ментални здравствени центри. Во Македонија постојат и бесплатни телефонски линии за поддршка."
    },
     "самодоверба": {
        "base": "Самодовербата е важно чувство за личен раст и успех. Работи на позитивна слика за себе и поставувај реални цели.",
        "tips": """Совети за подобрување на самодовербата:
1. Потсетувај се на своите достигнувања.
2. Поставувај мали, остварливи цели.
3. Окружи се со поддржувачки луѓе."""
    },
        "сон": {
        "base": "Квалитетниот сон е клучен за менталното здравје. Препорачливо е да имате редовен распоред за спиење и да избегнувате екраните пред спиење.",
        "tips": """Совети за подобар сон:
1. Одете на спиење и станувајте во исто време секој ден.
2. Избегнувајте кофеин и тешка храна навечер.
3. Креирајте смирувачка рутина пред спиење."""
    },
    "медитација": {
        "base": "Медитацијата помага во релаксација и намалување на анксиозност.",
        "techniques": """Популарни техники на медитација:
1. Медитација на внимание кон дишењето.
2. Водена медитација со звук.
3. Медитација со мантра."""
    },
    "анксиозност": {
        "base": "Анксиозноста може да се намали преку релаксациони вежби, когнитивна терапија и избегнување на стресори.",
        "techniques": """Техники за анксиозност:
1. Длабоко и свесно дишење.
2. Водени медитации.
3. Запишување на мисли и емоции."""
    },
    "депресија": {
        "base": "Депресијата е сериозно ментално здравје кое бара внимание, поддршка и понекогаш професионална помош.",
        "techniques": """Совети за депресија:
1. Редовна физичка активност.
2. Разговори со блиски лица или терапевт.
3. Избегнување алкохол и дроги."""
    },
    "осаменост": {
        "base": "Осаменоста може да се чувствува тешко, но постојат начини да се намали преку поврзување со други и самоподдршка.",
        "techniques": """Совети за осаменост:
1. Приклучи се на групи или клубови со заеднички интереси.
2. Разговарај со пријатели или членови на семејството.
3. Размисли за волонтирање за да запознаеш нови луѓе.
4. Води дневник за своите мисли и чувства."""
    },
    "default": "За подетални совети, контактирајте професионален психолошки советник."
}


def get_local_response(user_input):
    user_input = user_input.lower().strip()

    greetings = ["здраво", "добар ден"]
    thanks = ["благодарам", "фала", "ви благодарам"]
    farewells = ["пријатно", "поздрав", "чао"]

    if any(greet in user_input for greet in greetings):
        return "Здраво! Како можам да ти помогнам?"

    if any(thank in user_input for thank in thanks):
        return "Секако! Секогаш сум тука да ти помогнам."

    if any(farewell in user_input for farewell in farewells):
        return "Пријатно! Ако имаш уште прашања, слободно пиши ми."

    if "професионална помош" in user_input or "каде можам да побарам помош" in user_input:
        return LOCAL_EDUCATIONAL_DB["професионална помош"]["base"]

    for key in LOCAL_EDUCATIONAL_DB:
        if key in user_input:
            # Проверка дали корисникот бара дополнителни совети (пример, техника, совети)
            if any(word in user_input for word in ["пример", "техника", "техники", "совет", "совети"]):
                # Обиди се да вратиш 'techniques' или 'tips' ако постојат
                if "techniques" in LOCAL_EDUCATIONAL_DB[key]:
                    return LOCAL_EDUCATIONAL_DB[key]["techniques"]
                elif "tips" in LOCAL_EDUCATIONAL_DB[key]:
                    return LOCAL_EDUCATIONAL_DB[key]["tips"]
                else:
                    return LOCAL_EDUCATIONAL_DB[key]["base"]
            return LOCAL_EDUCATIONAL_DB[key]["base"]

    return LOCAL_EDUCATIONAL_DB["default"]



def get_chatbot_response(user_input):
    local_answer = get_local_response(user_input)
    if local_answer != LOCAL_EDUCATIONAL_DB["default"]:
        return local_answer

    if OPENAI_KEY:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers in Macedonian language."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAI Error:", e)
            traceback.print_exc()
            return "Се случи грешка при поврзување со OpenAI API. Обидете се повторно подоцна."
    else:
        return LOCAL_EDUCATIONAL_DB["default"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"response": "Ве молам внесете прашање."})

        answer = get_chatbot_response(user_input)
        return jsonify({"response": answer})
    except Exception as e:
        print("General Error:", e)
        traceback.print_exc()
        return jsonify({"response": "Се случи грешка. Обидете се повторно."})

if __name__ == "__main__":
    app.run(debug=True)
