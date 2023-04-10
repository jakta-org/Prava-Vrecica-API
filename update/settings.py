from pathlib import Path
from PravaVrecica import settings as proj_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AI_MODELS_DIR =  proj_settings.MEDIA_ROOT / 'ai_models'

# Constants for the AI models
MAX_FILES_STORED = 3

# Default values for the AI models
REGEX_VERSION = r'^\d+\.\d+\.\d+$'      # regex for the version number
DEFAULT_VERSION = '1.0.0'               # default version for the first AI model
AI_FILE_EXTENSION = '.h5'               # file extension for the AI models
ACCEPT_NONE_VERSION_UPLOAD = False      # if True, the version will be automatically incremented
ACCEPT_VERSION_REUPLOAD = True          # if True, the file will be overwritten