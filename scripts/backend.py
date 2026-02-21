from flask import Flask, request, render_template, url_for, jsonify, session
from utils.skin_utils import get_output_local, get_skin_local
from dotenv import load_dotenv
from datetime import timedelta
import skin_gen
import os
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_KEY")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=31)

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/gen', methods=['GET'])
def gen():
    return render_template('gen.html')

@app.route('/search/', methods=['GET'])
@app.route('/search', methods=['GET'])
@app.route('/search/<username>', methods=['GET'])
def search(username = "a"):
    return render_template('search.html', username = username)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    
    skin_gen.generate_skin(prompt, get_uuid())
    
    return jsonify({"success": True, "img_url": get_output_local(get_uuid())})

@app.route('/get-skin', methods=['POST'])
def get_skin_serv():
    skin = get_skin_local(get_uuid())
    return jsonify({
        "status": skin[0],
        "skin": skin[1]
    })

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]

if __name__ == "__main__":
    #host 0.0.0.0 to access it on other devices on the same network, not suited for production
    app.run(debug=True, use_reloader=False, host = "0.0.0.0")