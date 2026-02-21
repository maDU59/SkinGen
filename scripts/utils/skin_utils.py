import os
from utils.path_utils import PLACEHOLDER_DIR, OUTPUT_DIR

def get_skin(uuid = None, additional = "", hasToExist = True):
    skin = get_output(uuid, additional)
    if os.path.exists(skin) or not hasToExist:
        return "success", skin
    else:
        return "404", get_default_output(additional)

def get_output(uuid = None, additional = ""):
    if additional != "": additional = "_" + additional
    return OUTPUT_DIR + f"/{uuid}/skin{additional}.png"

def get_default_output(additional = ""):
    if additional != "": additional = "_" + additional
    return PLACEHOLDER_DIR + f"/default_skin{additional}.png"

def get_skin_local(uuid = None, additional = "", hasToExist = True):
    skin = get_output(uuid, additional)
    skin_local = get_output_local(uuid, additional)
    if os.path.exists(skin) or not hasToExist:
        return "success", skin_local
    else:
        return "404", get_default_output_local(additional)

def get_output_local(uuid = None, additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/output/{uuid}/skin{additional}.png"

def get_default_output_local(additional = ""):
    if additional != "": additional = "_" + additional
    return f"static/placeholders/default_skin{additional}.png"