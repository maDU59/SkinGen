import os.path as path

# The Root of your project
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

# Universal Paths
MASKS_DIR = path.join(BASE_DIR, "masks")
STATIC_DIR = path.join(BASE_DIR, "static")
OUTPUT_DIR = path.join(STATIC_DIR, "output")
PLACEHOLDER_DIR = path.join(STATIC_DIR, "placeholders")

# Specific Files
MASK_FILE = path.join(MASKS_DIR, "mask2.png")
DEFAULT_SKIN = path.join(PLACEHOLDER_DIR, "default_skin.png")