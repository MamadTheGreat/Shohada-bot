from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    print(update)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(port=8000)
