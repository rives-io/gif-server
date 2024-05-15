from redis import Redis
from flask import Flask, make_response, request, Response
from flask_cors import cross_origin
import base64

REDIS_GIFS_KEY = "tape_gifs"
REDIS_IMAGES_KEY = "tape_images"

redis = Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)

@app.route("/insert-gif", methods=["POST"])
@cross_origin()
def insert_gif():
    insert_obj = request.get_json()

    gameplay_id = insert_obj.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    gif = insert_obj.get("gif")
    if not gif: return make_response("Missing \"gif\" key!\n", 200)

    redis.hset(REDIS_GIFS_KEY,gameplay_id, gif)

    return make_response("Gif inserted\n", 200)

@app.route("/gifs", methods=["POST"])
@cross_origin()
def query_gifs():
    gameplays = request.get_json()

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
    insert_obj = request.get_json()

    gameplay_id = insert_obj.get("gameplay_id")
    if not gameplay_id: return make_response("Missing \"gameplay_id\" key!\n", 200)

    image = insert_obj.get("image")
    if not image: return make_response("Missing \"image\" key!\n", 200)

    redis.hset(REDIS_IMAGES_KEY, gameplay_id, image)

    return make_response("Image inserted\n", 200)

@app.route("/images", methods=["POST"])
@cross_origin()
def query_images():
    gameplays = request.get_json()

    images = redis.hmget(REDIS_IMAGES_KEY,gameplays)

    return images

@app.route("/images/<image_id>", methods=["GET"])
@cross_origin()
def query_image(image_id):
    data = base64.b64decode(redis.hget(REDIS_IMAGES_KEY,image_id))
    return Response(data, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)