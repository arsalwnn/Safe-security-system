# config.py

# =========================
# CAMERA CONFIG
# =========================
VIDEO_SOURCE = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# =========================
# MODEL PATHS
# =========================
SAFE_MODEL_PATH = "C:\\Users\\arsal\\OneDrive\\Desktop\\cctv_project\\best.pt"
PERSON_MODEL_PATH = "models/yolov8n.pt"

# =========================
# ZONE SETTINGS
# =========================
SAFE_ZONE_PADDING = 160

# =========================
# FACE RECOGNITION
# =========================
FACE_MATCH_THRESHOLD = 0.45   # سخت‌گیرانه‌تر از 0.5 قبلی
FACE_CHECK_INTERVAL = 0.5     # ثانیه (قبلاً frame-based بود، الان time-based)

# =========================
# INTRUDER SETTINGS
# =========================
INTRUDER_TIME_THRESHOLD = 5   # ثانیه

# =========================
# ALERT SETTINGS
# =========================
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "YOUR_APP_PASSWORD_HERE"
EMAIL_RECEIVER = "your_email@gmail.com"

# =========================
# STORAGE
# =========================
EVIDENCE_DIR = "evidence/"

# =========================
# SAFE MONITORING
# =========================
SAFE_MISSING_THRESHOLD = 3    # ثانیه
SAFE_MOVEMENT_THRESHOLD = 50  # پیکسل

# =========================
# ALERT COOLDOWN
# =========================
ALERT_COOLDOWN = 30           # ثانیه - حداقل فاصله بین دو alert