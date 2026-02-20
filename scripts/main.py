import backend
from backend import session, app
import skin_gen
import os
import uuid

def get_skin():
    skin = get_output()
    if os.path.exists(skin):
        return "success", skin
    else:
        return "404", get_default_output()

def get_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())
    return session["uuid"]

def get_output(additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/output/skin_{get_uuid()}{additional}.png"

def get_default_output(additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/placeholders/default_skin_{additional}.png"

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)