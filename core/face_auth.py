import face_recognition
import os
import numpy as np
import cv2

class FaceAuth:
    def __init__(self, db_path="faces"):
        self.known_encodings = []
        self.THRESHOLD = 0.45

        if not os.path.exists(db_path):
            os.makedirs(db_path)

        for file in os.listdir(db_path):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            path = os.path.join(db_path, file)

            # cv2 مطمئن‌ترین روش برای لود uint8 RGB
            img = cv2.imread(path)
            if img is None:
                print(f"  [SKIP] {file} -> نتونست لود بشه")
                continue
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            locations = face_recognition.face_locations(image, model="hog")
            encodings = face_recognition.face_encodings(image, num_jitters=0)

            if len(encodings) > 0:
                self.known_encodings.append(encodings[0])
                print(f"  Loaded: {file}")

        print(f"Loaded {len(self.known_encodings)} authorized faces")

    def is_authorized(self, frame):
        """
        frame: BGR (خروجی cv2) - کل فریم یا crop شخص
        برمیگردونه: (bool, float) -> (مجاز است؟، درصد اطمینان)
        """
        if len(self.known_encodings) == 0:
            return False, 0.0

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb, model="hog")

            if len(locations) == 0:
                return False, 0.0

            
           
            encodings = face_recognition.face_encodings(rgb, num_jitters=0)
            best_confidence = 0.0
            # num_jitters=0
            #  یعنی هر چهره رو یه بار پردازش کن.
            #  عدد بالاتر دقت رو بیشتر می‌کنه ولی کندتره —
            #  برای سیستم ضعیف 0 بهتره.
            #
            for encoding in encodings:
                distances = face_recognition.face_distance(self.known_encodings, encoding)
                min_distance = np.min(distances)
                confidence = (1.0 - min_distance) * 100

                if min_distance < self.THRESHOLD:
                    return True, round(confidence, 1)

                if confidence > best_confidence:
                    best_confidence = confidence

            return False, round(best_confidence, 1)

        except Exception as e:
            print("Face error:", e)
            return False, 0.0