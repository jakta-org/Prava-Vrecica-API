from pathlib import Path
from PravaVrecica import settings as proj_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

FEEDBACK_DIR =  proj_settings.MEDIA_ROOT / 'feedback'