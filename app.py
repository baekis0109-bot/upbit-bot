from flask import Flask, request, jsonify
import os
import uuid
import hashlib
import jwt
import requests

app = Flask(__name__)

UPBIT_ACCESS_KEY = "VBdUIrPREBW0HasnxnzqaMCm51ZfXXnVMHh1Topn"
UPBIT_SECRET_KEY = "8zCCIn4uKFnEEIPsucF7UtiaoeHhyx3ZdX5LpSXv"

def make_query_string(data):
    return "&".join(f"{k}={v}" for k, v in data.items())

def make_auth_headers(body):
    query_string = make_query_string(body)
    query_hash = hashlib.sha512(query_string.encode()).hexdigest()

    payload = {
        "access_key": UPBIT_ACCESS_KEY,
        "nonce": str(uuid.uuid4()),
        "query_hash": query_hash,
        "query_hash_alg": "SHA512"
    }

    token = jwt.encode(payload, UPBIT_SECRET_KEY, algorithm="HS512")

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@app.route("/trade", methods=["POST"])
def trade():
    data = request.get_json()

    if data["action"] == "BUY":
        body = {
            "market": data["market"],
            "side": "bid",
            "ord_type": "price",
            "price": data["price"]
        }
    elif data["action"] == "SELL":
        body = {
            "market": data["market"],
            "side": "ask",
            "ord_type": "market",
            "volume": data["volume"]
        }
    else:
        return jsonify({"error": "invalid action"}), 400

    headers = make_auth_headers(body)

    res = requests.post(
        "https://api.upbit.com/v1/orders",
        json=body,
        headers=headers
    )

    if res.status_code in (200, 201):
        return jsonify(res.json()), 200
    return jsonify(res.json()), 400

@app.get("/")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
