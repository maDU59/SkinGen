from flask import request, render_template, jsonify, session, Blueprint
from project.utils.skin_utils import get_output_local, get_skin_local, get_gallery_dir, get_gallery_dir_local
from flask_login import login_required, current_user
from project.utils.path_utils import BASE_DIR
import project.skin_gen as skin_gen
import queue
import uuid
import threading
import time
import os

main = Blueprint('main', __name__)

skin_queue = queue.Queue()
tickets_counter = 0
finished_tickets_counter = 0
results = {}

@main.route('/home', methods=['GET'])
@main.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@main.route('/gen', methods=['GET'])
def gen():
    return render_template('gen.html')

@main.route('/search/', methods=['GET'])
@main.route('/search', methods=['GET'])
@main.route('/search/<username>', methods=['GET'])
def search(username = "a"):
    return render_template('search.html', username = username)

@main.route('/generate', methods=['POST'])
def generate():
    global tickets_counter
    uuid = get_uuid()
    if current_user.is_authenticated:
        id = current_user.id
    else:
        id = None
    if uuid in results:
        print(uuid, " made a request while already in queue")
        return jsonify({
            "status": "already_queued",
            "result": uuid,
            "id": id
        }), 202

    prompt = request.json.get('prompt')

    skin_queue.put((prompt, uuid))
    tickets_counter += 1

    results[uuid] = {"status": "queued",
        "result": "None",
        "id": id,
        "time": time.time()}

    return jsonify({
        "status": "queued",
        "result": uuid,
        "id": id
    }), 202

@main.route('/get-skin', methods=['GET'])
def get_skin_serv():
    skin = get_skin_local(get_uuid())
    return jsonify({
        "status": skin[0],
        "skin": skin[1]
    })

@main.route('/check-queue', methods=['GET'])
def is_in_queuue():
    uuid = get_uuid()
    return jsonify({
        "status": uuid in results,
        "uuid": uuid
    })

@main.route('/editor', methods=['GET'])
@main.route('/editor/<path:skin_url>', methods=['GET'])
def editor(skin_url = "/static/skins/default.png"):
    if not skin_url.startswith('/') and not skin_url.startswith('http'):
        skin_url = '/' + skin_url
    return render_template('editor.html', skin_url = skin_url)

@main.route('/saved-skins/<user_id>', methods=['GET'])
@login_required
def saved_skins(user_id):
    if user_id != str(current_user.id):
        return jsonify({"status": "error", "result": "Unauthorized"}), 403
    if not os.path.exists(get_gallery_dir(user_id)):
        return jsonify({"status": "Success", "skins": []}), 200
    skins = [get_gallery_dir_local(user_id) + skin for skin in os.listdir(get_gallery_dir(user_id))[::-1]]
    return jsonify({"status": "Success", "skins": skins}), 200

@main.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', tokens_remaining=current_user.tokens)

@main.route('/delete-skin', methods=['POST'])
@login_required
def delete_skin():
    path = request.json.get('skin')
    if current_user.is_authenticated and str(current_user.id) == path.split("/")[-2]:
        full_path = os.path.join(BASE_DIR, path)
        print(full_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return jsonify({"status": "Success"}), 200
        else:
            return jsonify({"status": "Error", "result": "Skin not found"}), 404
    else:
        return jsonify({"status": "Error", "result": "Unauthorized"}), 403

@main.route('/result/<ticket_id>', methods=['GET'])
def get_result(ticket_id):

    if ticket_id != session.get("uuid"):
        return jsonify({"status": "error", "result": "Unauthorized"}), 403

    data = results.get(ticket_id)
    
    if not data:
        return jsonify({
            "status": "error", 
            "result": "Ticket expired or not found"
            }), 404

    if data["status"] == "completed":
        results.pop(ticket_id) 
        return jsonify({
            "status": "completed", 
            "result": f"{data['result']}"
        })
    elif data["status"] == "failed":
        results.pop(ticket_id) 
        return jsonify({
            "status": "error", 
            "result": "Error while generating skin"
            }), 404
    
    return jsonify(data | {"queue_pos":tickets_counter - finished_tickets_counter - 1}), 202

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]

def worker():
    """
    Generate skins
    """
    global finished_tickets_counter
    while True:
        # This blocks until an item is available
        prompt, uuid = skin_queue.get()

        if uuid not in results:
            skin_queue.task_done()
            finished_tickets_counter += 1
            continue
        
        results[uuid]["status"] = "processing"
        results[uuid]["time"] = time.time()
        id = results[uuid].get("id", None)
        
        try:
            print(f"Processing: {uuid}")
            skin_gen.generate_skin(prompt, uuid, id)
            
            results[uuid]["result"] = get_output_local(uuid)
            results[uuid]["status"] = "completed"
            results[uuid]["time"] = time.time()
            print(f"Finished processing: {uuid}")
        except Exception as e:
            results[uuid]["status"] = "failed"
            results[uuid]["time"] = time.time()
        
        skin_queue.task_done()
        finished_tickets_counter += 1

worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

def cleaner():
    """
    Cleans up abandoned or old results to prevent memory leaks.
    """
    while True:
        time.sleep(300)
        now = time.time()
        for uuid in list(results.keys()):
            if now - results[uuid].get("time", 0) > 1200 and not results[uuid].get("status", "queued") in ["queued", "processing"]: #20 minutes
                del results[uuid]
                print(f"Cleaned up expired session {uuid}")

# Start the janitor thread alongside your worker
janitor_thread = threading.Thread(target=cleaner, daemon=True)
janitor_thread.start()