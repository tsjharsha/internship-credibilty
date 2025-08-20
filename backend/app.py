from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend (React) to talk to backend

@app.route("/")
def home():
    return jsonify({"message": "Backend is running ✅"})

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    link = data.get("link")
    description = data.get("description")
    email = data.get("email")

    # For now, just return the inputs back (mock response)
    return jsonify({
        "status": "success",
        "received": {
            "link": link,
            "description": description,
            "email": email
        },
        "credibility": "Looks okay (demo)"
    })

if __name__ == "__main__":
    app.run(debug=True)
