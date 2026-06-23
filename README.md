# 🔐 Safe Security System

A real-time AI-powered security system that monitors a safe using computer vision. It detects unauthorized persons near the safe, verifies their identity via face recognition, and sends instant alerts.

---

## 📸 How It Works

1. **Safe Detection** — A custom YOLOv8 model detects the safe in the camera frame
2. **Zone Creation** — A danger zone is drawn around the safe
3. **Person Detection** — YOLOv8n detects any person entering the zone
4. **Intruder Timer** — If someone stays in the zone for 5+ seconds, they're flagged
5. **Face Recognition** — The system checks if the person is authorized
6. **Alert** — If unauthorized, saves evidence and sends Telegram + Email alerts

## 🗂️ Dataset

- 80 images collected and manually labeled using **LabelImg**
- Split into train / validation / test sets
- Custom YOLOv8 model trained from scratch to detect safes
---

## 🛠️ Tech Stack

- **YOLOv8** (Ultralytics) — Object detection
- **face_recognition** + **dlib** — Face verification
- **OpenCV** — Camera feed and frame processing
- **Telegram Bot API** — Real-time photo alerts
- **Gmail SMTP** — Email alerts with evidence attachment

---

## 📁 Project Structure

```
cctv_project/
│
├── main.py                 # Entry point
├── alert.py                # Telegram & Email alert system
├── config.py               # All settings and credentials
├── requirements.txt
│
├── core/
│   ├── camera.py           # Camera wrapper
│   ├── detector.py         # YOLO detection (safe + person)
│   ├── face_auth.py        # Face recognition & authorization
│   ├── tracker.py          # Intruder timer logic
│   ├── safe_tracker.py     # Safe position smoothing (EMA)
│   └── zone.py             # Danger zone creation & overlap check
│
├── faces/                  # Authorized face images (not included)
├── evidence/               # Saved intruder snapshots (not included)
└── models/                 # YOLOv8 weights (not included)
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/arsalwnn/cctv_project.git
cd cctv_project
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your data
- Put authorized face images in `faces/` folder (jpg/png)
- Put your custom safe detection model (`best.pt`) in the root
- Edit `config.py` with your Telegram token, chat ID, and Gmail credentials

### 5. Run
```bash
python main.py
```

---

## 🔧 Configuration (`config.py`)

| Setting | Default | Description |
|---|---|---|
| `VIDEO_SOURCE` | `0` | Camera index or RTSP URL |
| `FACE_MATCH_THRESHOLD` | `0.45` | Lower = stricter face matching |
| `INTRUDER_TIME_THRESHOLD` | `5` | Seconds before flagging as intruder |
| `ALERT_COOLDOWN` | `30` | Seconds between alerts |
| `SAFE_ZONE_PADDING` | `160` | Danger zone size around safe (pixels) |

---

## 📬 Alert Example

When an intruder is detected:
- 📷 Evidence photo saved to `evidence/`
- 📱 Telegram message with photo sent instantly
- 📧 Email with attached photo sent to configured address

---

## 🚀 Future Improvements

- [ ] Multi-camera support
- [ ] Web dashboard for live monitoring
- [ ] Night vision / low-light enhancement
- [ ] Database logging of all events

---

## 👤 Author

**Amirarsalan Rezaianzadeh**  
[GitHub](https://github.com/arsalwnn)
