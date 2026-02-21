from flask import Flask, request, render_template, url_for, jsonify, session
from utils.skin_utils import get_output_local, get_skin_local
from dotenv import load_dotenv
from datetime import timedelta
import skin_gen
import queue
import os
import uuid
import threading

load_dotenv()

skin_queue = queue.Queue()
results = {}
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
    uuid = get_uuid()
    if uuid in results:
        print(uuid, " made a request while already in queue")
        return jsonify({
            "status": "already_queued",
            "result": uuid
        }), 202

    prompt = request.json.get('prompt')

    skin_queue.put((prompt, uuid))

    results[uuid] = {"status": "queued",
        "result": "None"}

    return jsonify({
        "status": "queued",
        "result": uuid
    }), 202

@app.route('/get-skin', methods=['POST'])
def get_skin_serv():
    skin = get_skin_local(get_uuid())
    return jsonify({
        "status": skin[0],
        "skin": skin[1]
    })

@app.route('/check-queue')
def is_in_queuue():
    uuid = get_uuid()
    return jsonify({
        "status": uuid in results,
        "uuid": uuid
    })

@app.route('/result/<ticket_id>')
def get_result(ticket_id):
    data = results.get(ticket_id)
    
    if not data:
        return jsonify({
            "status": "error", 
            "result": "Ticket expired or not found"
            }), 404

    if data["status"] == "completed":
        final_data = results.pop(ticket_id) 
        return jsonify({
            "status": "completed", 
            "result": f"{final_data['result']}"
        })
    elif data["status"] == "failed":
        return jsonify({
            "status": "error", 
            "result": "Error while generating skin"
            }), 404
    
    return jsonify(data), 202

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]

def worker():
    """
    Generate skins
    """
    while True:
        # This blocks until an item is available
        prompt, uuid = skin_queue.get()
        
        results[uuid]["status"] = "processing"
        
        try:
            print(f"Processing: {uuid}")
            skin_gen.generate_skin(prompt, uuid)
            
            results[uuid]["result"] = get_output_local(uuid)
            results[uuid]["status"] = "completed"
            print(f"Finished processing: {uuid}")
        except Exception as e:
            results[uuid]["status"] = "failed"
        
        skin_queue.task_done()

worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

if __name__ == "__main__":
    #host 0.0.0.0 to access it on other devices on the same network, not suited for production
    app.run(debug=True, use_reloader=False, host = "0.0.0.0")