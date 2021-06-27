import os
from flask import Flask, request, jsonify
from take_attendance import take_attendance

app = Flask(__name__)


@app.route("/", methods=['POST'])
def attendance():
    response = take_attendance(request)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))