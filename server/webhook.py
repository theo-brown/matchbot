from flask import Flask, request, Response
from subprocess import run

app = Flask(__name__)

@app.route('/tournabot-webhook', methods=['POST'])
def respond():
    payload = request.json
    if payload.ref == "refs/head/master":
        print("Pulling repo....")
        run("./bot_update.sh")        
    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True)