from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Store your OpenAI key in an environment variable
SECRET_KEY = os.environ.get("OUTLOOK_SECRET", "your_custom_secret_key_here")

@app.route("/generate", methods=["POST"])
def generate_reply():
    if request.headers.get("x-api-key") != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    email = data.get("email", "")
    tone = data.get("tone", "professional")

    prompt = f"Write a {tone.lower()} reply to this email:

{email}

---
Reply:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        text = response.choices[0].message['content']
        replies = text.strip().split("

")  # Simple split if multiple replies are returned
        return jsonify({"replies": replies})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check-origin", methods=["POST"])
def check_origin():
    if request.headers.get("x-api-key") != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    email = request.json.get("email", "")
    prompt = f"Determine if the following email text was likely written by a human or by AI. Provide a simple answer like 'AI-generated (confidence: 87%)' or 'Human-written (confidence: 92%)'.

{email}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=60
        )
        result = response.choices[0].message['content'].strip()
        return jsonify({"origin": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
