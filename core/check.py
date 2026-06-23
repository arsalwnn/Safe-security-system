import face_recognition
import os

class FaceAuth:
    def __init__(self, db_path="faces"):
        self.known_encodings = []

        if not os.path.exists(db_path):
            os.makedirs(db_path)

        for file in os.listdir(db_path):
            path = os.path.join(db_path, file)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                self.known_encodings.append(encodings[0])

        print(f"Loaded {len(self.known_encodings)} authorized faces")

    def is_authorized(self, frame):
        try:
            rgb = frame[:, :, ::-1]

            # فقط خود library صورت رو پیدا کنه
            encodings = face_recognition.face_encodings(rgb)

            if len(encodings) == 0:
                return False

            for encoding in encodings:
                matches = face_recognition.compare_faces(self.known_encodings, encoding)

                if True in matches:
                    return True

            return False

        except Exception as e:
            print("Face error:", e)
            return False
        -------------
        import cv2
import time

from core.camera import Camera
from core.detector import Detector
from config import SAFE_MODEL_PATH, PERSON_MODEL_PATH
from core.zone import create_zone, is_inside
from core.tracker import IntruderTracker
from core.face_auth import FaceAuth

camera = Camera()
detector = Detector(SAFE_MODEL_PATH, PERSON_MODEL_PATH)
tracker = IntruderTracker()
face_auth = FaceAuth()

last_check_time = 0
CHECK_INTERVAL = 2  # هر 2 ثانیه
last_auth_result = False

while True:
    ret, frame = camera.read()
    if not ret:
        break

    safes = detector.detect_safe(frame)
    persons = detector.detect_person(frame)

    if len(safes) > 0:
        safe_bbox = max(safes, key=lambda x: (x[2]-x[0])*(x[3]-x[1]))[:4]

        x1, y1, x2, y2 = safe_bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # =========================
        # ZONE
        # =========================
        zone = create_zone(safe_bbox, padding=160)
        zx1, zy1, zx2, zy2 = zone
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)

        # =========================
        # آیا کسی داخل زون هست؟
        # =========================
        any_inside = any(is_inside(p, zone) for p in persons)

        # =========================
        # TIMER (5 ثانیه)
        # =========================
        intruder = tracker.update(any_inside)

        # =========================
        # ✅ Face Recognition فقط یکبار روی کل فریم
        # =========================
        current_time = time.time()
        if any_inside and (current_time - last_check_time > CHECK_INTERVAL):
            last_auth_result = face_auth.is_authorized(frame)
            last_check_time = current_time

        if not any_inside:
            last_auth_result = False

        # =========================
        # رسم افراد
        # =========================
        for person in persons:
            px1, py1, px2, py2 = person
            inside = is_inside(person, zone)

            if intruder and inside:
                if last_auth_result:
                    color = (255, 0, 0)
                    label = "AUTHORIZED"
                else:
                    color = (0, 0, 255)
                    label = "INTRUDER!"

            elif inside:
                color = (0, 165, 255)
                label = "IN ZONE"

            else:
                color = (0, 255, 255)
                label = "PERSON"

            cv2.rectangle(frame, (px1, py1), (px2, py2), color, 2)
            cv2.putText(frame, label, (px1, py1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    else:
        tracker.update(False)
        last_auth_result = False

        for (x1, y1, x2, y2) in persons:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

    cv2.imshow("Safe Security System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
---------------------
import cv2
import time

from core.camera import Camera
from core.detector import Detector
from core.zone import create_zone, is_inside
from core.tracker import IntruderTracker
from core.face_auth import FaceAuth
from alert import AlertSystem
from config import *

# ─── Init ────────────────────────────────────────────────────────────────────
camera = Camera()
detector = Detector(SAFE_MODEL_PATH, PERSON_MODEL_PATH)
tracker = IntruderTracker()
face_auth = FaceAuth()
alert = AlertSystem()

last_check_time = 0
last_auth_result = False
last_confidence = 0.0

# ─── Main Loop ───────────────────────────────────────────────────────────────
while True:
    ret, frame = camera.read()
    if not ret:
        break

    safes = detector.detect_safe(frame)
    persons = detector.detect_person(frame)

    if len(safes) > 0:
        # بزرگ‌ترین safe رو انتخاب کن (نزدیک‌ترین به دوربین)
        safe_bbox = max(safes, key=lambda x: (x[2]-x[0]) * (x[3]-x[1]))[:4]
        x1, y1, x2, y2 = safe_bbox

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "SAFE", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # ── Zone ──────────────────────────────────────────────────────────
        zone = create_zone(safe_bbox, padding=SAFE_ZONE_PADDING)
        zx1, zy1, zx2, zy2 = zone
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 1)

        # ── افراد داخل zone ───────────────────────────────────────────────
        persons_in_zone = [p for p in persons if is_inside(p, zone)]
        any_inside = len(persons_in_zone) > 0

        # ── Intruder timer ────────────────────────────────────────────────
        intruder = tracker.update(any_inside)

        # ── Face auth روی crop بزرگ‌ترین شخص داخل zone ───────────────────
        current_time = time.time()
        if any_inside and (current_time - last_check_time > FACE_CHECK_INTERVAL):
            target = max(persons_in_zone, key=lambda p: (p[2]-p[0]) * (p[3]-p[1]))
            px1, py1, px2, py2 = target

            h, w = frame.shape[:2]
            pad = 20
            crop = frame[max(0, py1-pad):min(h, py2+pad),
                         max(0, px1-pad):min(w, px2+pad)]

            if crop.size > 0:
                last_auth_result, last_confidence = face_auth.is_authorized(crop)
                last_check_time = current_time

        if not any_inside:
            last_auth_result = False
            last_confidence = 0.0

        # ── Alert: فقط وقتی intruder هست و authorize نشده ─────────────────
        if intruder and any_inside and not last_auth_result:
            alert.trigger(frame)

        # ── رسم افراد ─────────────────────────────────────────────────────
        for person in persons:
            px1, py1, px2, py2 = person
            inside = is_inside(person, zone)

            if intruder and inside:
                if last_auth_result:
                    color = (0, 200, 0)
                    label = f"AUTHORIZED ({last_confidence}%)"
                else:
                    color = (0, 0, 255)
                    label = f"INTRUDER! ({last_confidence}%)"
            elif inside:
                color = (0, 165, 255)
                label = "IN ZONE"
            else:
                color = (0, 255, 255)
                label = "PERSON"

            cv2.rectangle(frame, (px1, py1), (px2, py2), color, 2)
            cv2.putText(frame, label, (px1, py1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    else:
        # Safe پیدا نشد
        tracker.update(False)
        last_auth_result = False
        last_confidence = 0.0

        for (x1, y1, x2, y2) in persons:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cv2.putText(frame, "Safe not detected", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Safe Security System", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

camera.release()
cv2.destroyAllWindows()
-----------
ine 
import cv2
import time

from core.camera import Camera
from core.detector import Detector
from config import SAFE_MODEL_PATH, PERSON_MODEL_PATH
from core.zone import create_zone, is_inside
from core.tracker import IntruderTracker
from core.face_auth import FaceAuth

camera = Camera()
detector = Detector(SAFE_MODEL_PATH, PERSON_MODEL_PATH)
tracker = IntruderTracker()
face_auth = FaceAuth()

last_check_time = 0
CHECK_INTERVAL = 0.5  # هر نیم ثانیه (قبلاً 2 ثانیه بود)
last_auth_result = False
last_confidence = 0.0

while True:
    ret, frame = camera.read()
    if not ret:
        break

    safes = detector.detect_safe(frame)
    persons = detector.detect_person(frame)

    if len(safes) > 0:
        safe_bbox = max(safes, key=lambda x: (x[2]-x[0])*(x[3]-x[1]))[:4]

        x1, y1, x2, y2 = safe_bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # =========================
        # ZONE
        # =========================
        zone = create_zone(safe_bbox, padding=160)
        zx1, zy1, zx2, zy2 = zone
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)

        # =========================
        # آیا کسی داخل زون هست؟
        # =========================
        persons_in_zone = [p for p in persons if is_inside(p, zone)]
        any_inside = len(persons_in_zone) > 0

        # =========================
        # TIMER
        # =========================
        intruder = tracker.update(any_inside)

        # =========================
        # Face Recognition فقط روی crop شخص داخل zone
        # =========================
        current_time = time.time()

        if any_inside and (current_time - last_check_time > CHECK_INTERVAL):
            # فقط بزرگ‌ترین شخص داخل zone رو چک کن
            target = max(persons_in_zone, key=lambda p: (p[2]-p[0])*(p[3]-p[1]))
            px1, py1, px2, py2 = target

            # کمی padding اضافه کن تا چهره کامل‌تر باشه
            h, w = frame.shape[:2]
            pad = 20
            cx1 = max(0, px1 - pad)
            cy1 = max(0, py1 - pad)
            cx2 = min(w, px2 + pad)
            cy2 = min(h, py2 + pad)

            cropped = frame[cy1:cy2, cx1:cx2]

            if cropped.size > 0:
                last_auth_result, last_confidence = face_auth.is_authorized(cropped)
                last_check_time = current_time

        if not any_inside:
            last_auth_result = False
            last_confidence = 0.0

        # =========================
        # رسم افراد
        # =========================
        for person in persons:
            px1, py1, px2, py2 = person
            inside = is_inside(person, zone)

            if intruder and inside:
                if last_auth_result:
                    color = (255, 165, 0)  # نارنجی
                    label = f"AUTHORIZED ({last_confidence}%)"
                else:
                    color = (0, 0, 255)
                    label = f"INTRUDER! ({last_confidence}%)"

            elif inside:
                color = (0, 165, 255)
                label = "IN ZONE"

            else:
                color = (0, 255, 255)
                label = "PERSON"

            cv2.rectangle(frame, (px1, py1), (px2, py2), color, 2)
            cv2.putText(frame, label, (px1, py1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    else:
        tracker.update(False)
        last_auth_result = False
        last_confidence = 0.0

        for (x1, y1, x2, y2) in persons:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

    cv2.imshow("Safe Security System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
