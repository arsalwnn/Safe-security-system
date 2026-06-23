from ultralytics import YOLO

class Detector:
    def __init__(self, safe_model_path, person_model_path):
        self.safe_model = YOLO(safe_model_path)
        self.person_model = YOLO(person_model_path)

    def detect_safe(self, frame):
        results = self.safe_model(frame, verbose=False)
        safes = []


        frame_area = frame.shape[0] * frame.shape[1]

        
        for r in results:
            for box, conf in zip(r.boxes, r.boxes.conf):
                conf = float(conf)

                if conf < 0.7:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # ❗ حذف باکس‌های خیلی بزرگ (مثل سقف)
                box_area = (x2 - x1) * (y2 - y1)
                if box_area > frame_area * 0.5:
                    continue

                safes.append((x1, y1, x2, y2, conf))

        return safes

    def detect_person(self, frame):
        results = self.person_model(frame, verbose=False)
        persons = []

        for r in results:
            for box, cls in zip(r.boxes, r.boxes.cls):
                if int(cls) == 0:  # class 0 = person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    persons.append((x1, y1, x2, y2))

        return persons