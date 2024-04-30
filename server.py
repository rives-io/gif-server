import hashlib
import os
from redis import Redis
from flask import Flask, make_response, request, jsonify
from flask_cors import cross_origin
import jwt
import json

redis = Redis(host='localhost', port=6379, decode_responses=True)
SECRET_KEY = None

app = Flask(__name__)

@app.route("/insert-gif", methods=["POST"])
@cross_origin()
def insert_gif():
    insert_obj = request.get_json()

    gameplay_id = insert_obj.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    gif = insert_obj.get("gif")
    if not gif: return make_response("Missing \"gif\" key!\n", 200)

    redis.set(gameplay_id, gif)

    return make_response("Inserted\n", 200)

@app.route("/gifs", methods=["POST"])
@cross_origin()
def query_gifs():
    gameplays = request.get_json()

    gifs = redis.mget(gameplays)

    return gifs

@app.route("/useCode", methods=["POST"])
@cross_origin()
def useCode():
    global SECRET_KEY

    payload = request.get_json()
    encodedCodeSession = payload.get("codeSession")
    if not encodedCodeSession: return make_response("Missing \"codeSession\" key!\n", 200)

    decoded_payload = None
    try:
        decoded_payload = jwt.decode(encodedCodeSession, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

    code = decoded_payload.get("code")
    if not code: return jsonify({"success": False, "msg": "Missing \"codeHash\" key!"})

    userAddress = decoded_payload.get("userAddress")
    if not userAddress: return jsonify({"success": False, "msg": "Missing \"userAddress\" key!\n"})

    codeHash = calculateCodeHash(code.lower())
    codeOwner = redis.get(codeHash)

    if codeOwner is None: return jsonify({"success": False, "msg": "Invalid code!"})
    if len(codeOwner) > 0:
        if codeOwner != userAddress.lower(): return jsonify({"success": False, "msg": "Code already taken!"})
        else: return jsonify({"success": True, "msg": "Code verified."})

    redis.set(codeHash, userAddress.lower())

    return jsonify({"success": True, "msg": "Code used."})

@app.route("/validateCode", methods=["POST"])
@cross_origin()
def validateCode():
    global SECRET_KEY

    payload = request.get_json()
    encodedCodeSession = payload.get("codeSession")
    if not encodedCodeSession: return make_response("Missing \"codeSession\" key!\n", 200)

    decoded_payload = None
    try:
        decoded_payload = jwt.decode(encodedCodeSession, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

    code = decoded_payload.get("code")
    if not code: return make_response("Missing \"code\" key!\n", 200)

    codeHash = calculateCodeHash(code.lower())
    codeOwner = redis.get(codeHash)

    if codeOwner is None: return jsonify({"success": False, "msg": "Invalid code!"})

    return jsonify({"success": True, "msg": "Code Validated."})

def loadCodes(filename="local.config.json"):
    global SECRET_KEY

    with open(filename, "r") as f:
        obj = json.load(f)
        
        key = obj.get("key")
        codes = obj.get("codes")
        if not key: raise Exception(f"Missing JWT Secret Key. Add the \"key\" field to {filename}")
        if not codes: raise Exception("Missing invite codes list. Add the \"codes\" field to {filename}")
        SECRET_KEY = key
        
        for code in codes:
            codeHash = calculateCodeHash(code)
            taken = redis.get(codeHash)

            if taken: redis.set(codeHash, taken)
            else: redis.set(codeHash, "")


def calculateCodeHash(code):
    sha256 = hashlib.sha256()
    sha256.update(code.encode())
    return sha256.hexdigest().lower()

if __name__ == "__main__":
    production = os.path.exists("config.json")
    if production: loadCodes("config.json")
    else: loadCodes()
    app.run(host="0.0.0.0", port=8000, debug=True)