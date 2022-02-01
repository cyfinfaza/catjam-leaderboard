from datetime import datetime
from flask import Flask, request, Response, render_template
from flask_cors import CORS
import pymongo
import dotenv
from os import environ
import json

dotenv.load_dotenv()
MONGODB_SECRET = environ.get("MONGODB_CONNSTRING")

client = pymongo.MongoClient(MONGODB_SECRET)
db = client.gamedata
leaderboardCollection = db.leaderboard

app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)


def success_json(data=None):
    if data != None:
        return Response(
            json.dumps({"status": "success", "data": data}),
            status=200,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps({"status": "success"}), status=200, mimetype="application/json"
        )


def error_json(error=None):
    if error != None:
        return Response(
            json.dumps({"status": "error", "error": error}),
            status=400,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps({"status": "error"}), status=400, mimetype="application/json"
        )


def fetchLeaderboard():
    leaderboard = (
        leaderboardCollection.find().sort("score", pymongo.DESCENDING).limit(5)
    )
    leaderboard = [
        {"score": x["score"], "initials": x["initials"]} for x in leaderboard
    ]
    return leaderboard


@app.route("/")
def index():
    return render_template("leaderboard.html", scores=fetchLeaderboard())


@app.route("/reportScore", methods=["PUT"])
def report():
    print(request.data)
    data = request.get_json(force=True)
    if data and "score" in data and "initials" in data:
        if not (isinstance(data["initials"], str) and isinstance(data["score"], int)):
            return error_json("Invalid types, must be string and int")
        if len(data["initials"]) != 3:
            return error_json("Initials must be 3 characters or less")
        if data["score"] < 0 or data["score"] > 999:
            return error_json("Score must be between 0 and 999")
        numAboveScore = leaderboardCollection.count_documents(
            {"score": {"$gte": data["score"]}}
        )
        if numAboveScore > 4:
            return error_json("Score must be greater than the #5 score")
        else:
            ip = (
                request.headers["x-real-ip"]
                if "x-real-ip" in request.headers
                else "unknown"
            )
            leaderboardCollection.update_one(
                {"initials": data["initials"]},
                {
                    "$set": {
                        "score": data["score"],
                        "initials": data["initials"].upper(),
                        "timestamp": datetime.utcnow(),
                        "ip": ip,
                    }
                },
                upsert=True,
            )
            return success_json()
    else:
        return error_json("Malformed request")


@app.route("/leaderboard")
def leaderboard():
    return success_json(fetchLeaderboard())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
