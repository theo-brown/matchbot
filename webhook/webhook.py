from flask import Flask, request, Response
import subprocess

app = Flask(__name__)

@app.route('/tournabot-webhook', methods=['POST'])
def respond():
    payload = request.get_json()
    print(payload["ref"])
    if payload["ref"] == "refs/heads/main":
        print("Pulling repo....")
        subprocess.run("./bot_update.sh", shell=True)
    return Response(status=200)
