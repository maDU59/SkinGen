from flask import Flask, request, render_template, url_for, jsonify, session
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

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    
    skin_gen.generate_skin(prompt)
    
    return jsonify({"success": True, "img_url": get_output()})

@app.route('/get-skin', methods=['POST'])
def return_skin():
    skin = get_output()
    if os.path.exists(skin):
        return jsonify({
            "status": "success",
            "skin": skin
        })
    else:
        return jsonify({
            "status": "404",
            "skin": skin
        })

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]

def get_output(additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/output/skin_{get_uuid()}{additional}.png"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)