from redis import Redis
from flask import Flask, make_response, request
from flask_cors import cross_origin

redis = Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)

@app.route("/insert-gif", methods=["POST"])
@cross_origin()
def insert_gif():
    insert_obj = request.get_json()

    gameplay_id = insert_obj.get("gameplay_id")
    if not gameplay_id: return "Missing \"gameplay_id\" key!"

    gif = insert_obj.get("gif")
    if not gif: return "Missing \"gif\" key!"

    redis.set(gameplay_id, gif)

    return make_response("Inserted\n", 200)

@app.route("/gifs", methods=["POST"])
@cross_origin()
def query_gifs():
    gameplays = request.get_json()

    gifs = redis.mget(gameplays)
    print(gifs)

    return gifs




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)