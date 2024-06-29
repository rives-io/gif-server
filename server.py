from redis import Redis
from flask import Flask, jsonify, make_response, request, Response
from flask_cors import cross_origin
import base64
import os
import jwt

REDIS_GIFS_KEY = "tape_gifs"
REDIS_IMAGES_KEY = "tape_images"
REDIS_NAMES_KEY = "tape_names"

SECRET = os.getenv("SECRET")

redis = Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)

@app.route("/insert-gif", methods=["POST"])
@cross_origin()
def insert_gif():
    global SECRET

    if request.content_length > 1000000:
        return make_response("Content too large.", 200)
    payload = request.get_data()

    decoded_payload = None
    try:
        decoded_payload = jwt.decode(payload, SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


    gameplay_id = decoded_payload.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    gif = decoded_payload.get("gif")
    if not gif: return make_response("Missing \"gif\" key!\n", 200)

    redis.hset(REDIS_GIFS_KEY,gameplay_id, gif)

    return make_response("Gif inserted\n", 200)

@app.route("/gifs", methods=["POST"])
@cross_origin()
def query_gifs():
    gameplays = request.get_json()
    if len(gameplays) == 0: return make_response("Missing gameplays IDs.", 200)

    gifs = redis.hmget(REDIS_GIFS_KEY,gameplays)

    return gifs

@app.route("/gifs/<gif_id>", methods=["GET"])
@cross_origin()
def query_gif(gif_id):
    data = base64.b64decode(redis.hget(REDIS_GIFS_KEY,gif_id))
    return Response(data, mimetype='image/gif')

@app.route("/insert-image", methods=["POST"])
@cross_origin()
def insert_image():
    global SECRET

    if request.content_length > 600000:
        return make_response("Content too large.", 200)
    payload = request.get_data()

    decoded_payload = None
    try:
        decoded_payload = jwt.decode(payload, SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

    gameplay_id = decoded_payload.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    image = decoded_payload.get("image")
    if not image: return make_response("Missing \"image\" key!\n", 200)

    redis.hset(REDIS_IMAGES_KEY, gameplay_id, image)

    return make_response("Image inserted\n", 200)

@app.route("/images", methods=["POST"])
@cross_origin()
def query_images():
    gameplays = request.get_json()
    if len(gameplays) == 0: return make_response("Missing gameplays IDs.", 200)

    images = redis.hmget(REDIS_IMAGES_KEY,gameplays)

    return images

@app.route("/images/<image_id>", methods=["GET"])
@cross_origin()
def query_image(image_id):
    data = base64.b64decode(redis.hget(REDIS_IMAGES_KEY,image_id))
    return Response(data, mimetype='image/png')


@app.route("/insert-name", methods=["POST"])
@cross_origin()
def insert_name():
    global SECRET

    if request.content_length > 400:
        return make_response("Content too large.", 200)
    payload = request.get_data()

    decoded_payload = None
    try:
        decoded_payload = jwt.decode(payload, SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

    gameplay_id = decoded_payload.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    name = decoded_payload.get("name")
    if not name: return make_response("Missing \"name\" key!\n", 200)

    redis.hset(REDIS_NAMES_KEY, gameplay_id, name)

    return make_response("Name inserted\n", 200)

@app.route("/names", methods=["POST"])
@cross_origin()
def query_names():
    gameplays = request.get_json()
    if len(gameplays) == 0: return make_response("Missing gameplays IDs.", 200)

    images = redis.hmget(REDIS_NAMES_KEY,gameplays)

    return images

@app.route("/names/<gameplay_id>", methods=["GET"])
@cross_origin()
def query_name(gameplay_id):
    data = redis.hget(REDIS_NAMES_KEY,gameplay_id)
    return Response(data, mimetype='image/png')

if __name__ == "__main__":
    if SECRET is None:
        raise Exception("Missing declaration of 'SECRET' env variable.")

    app.run(host="0.0.0.0", port=8000, debug=True)