from flask import Flask, request, Response
import subprocess

app = Flask(__name__)

@app.route('/tournabot-webhook', methods=['POST'])
def respond():
    payload = request.json
    if payload['ref'] == "refs/head/master":
        print("Pulling repo....")
        subprocess.run("./bot_update.sh", shell=True)        
    return Response(status=200)
