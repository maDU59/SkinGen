from flask import Flask, request, render_template, url_for, jsonify, session
from utils.skin_utils import get_output, get_skin
import skin_gen
import os
import uuid
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_KEY")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=31)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_no_arg():
    return render_template('search.html', username = "a")

@app.route('/search/<username>', methods=['GET'])
def search(username):
    return render_template('search.html', username = username)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    
    skin_gen.generate_skin(prompt, get_uuid())
    
    return jsonify({"success": True, "img_url": get_output(get_uuid())})

@app.route('/get-skin', methods=['POST'])
def get_skin_serv():
    skin = get_skin(get_uuid())
    return jsonify({
        "status": skin[0],
        "skin": skin[1]
    })

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]