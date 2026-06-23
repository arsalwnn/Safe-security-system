# core/tracker.py

import time

class IntruderTracker:
    def __init__(self, threshold=5):
        self.start_time = None
        self.threshold = threshold

    def update(self, inside_zone):
        if inside_zone:
            if self.start_time is None:
                self.start_time = time.time()

            elapsed = time.time() - self.start_time

            if elapsed > self.threshold:
                return True  # Intruder detected

        else:
            self.start_time = None

        return False