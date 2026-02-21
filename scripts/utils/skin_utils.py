import os

def get_skin(uuid = None, additional = "", hasToExist = True):
    skin = get_output(uuid, additional)
    if os.path.exists(skin) or not hasToExist:
        return "success", skin
    else:
        return "404", get_default_output(additional)

def get_output(uuid = None, additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/output/{uuid}/skin{additional}.png"

def get_default_output(additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/placeholders/default_skin{additional}.png"