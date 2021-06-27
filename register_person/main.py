import os
from flask import Flask, request, jsonify
from register_person import register_person

app = Flask(__name__)


@app.route("/", methods=['POST'])
def register():
    response = register_person(request)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))