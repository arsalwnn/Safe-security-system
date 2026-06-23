# core/safe_tracker.py

class SafeTracker:
    def __init__(self, alpha=0.2, max_missing=10):
        self.prev_bbox = None
        self.alpha = alpha
        #ضریب 
        # EMA (Exponential Moving Average). وقتی گاوصندوق بین فریم‌ها
        #  کمی جابجا میشه (لرزش دوربین)، 
        # به جای اینکه باکس بپره، آروم آروم حرکت کنه.
        self.missing_frames = 0
        self.max_missing = max_missing

    def update(self, detections):
        # اگر detection داریم
        if len(detections) > 0:
            self.missing_frames = 0

            # بهترین detection (بیشترین confidence)
            best = max(detections, key=lambda x: x[4])
            x1, y1, x2, y2, _ = best

            if self.prev_bbox is None:
                self.prev_bbox = (x1, y1, x2, y2)
            else:
                px1, py1, px2, py2 = self.prev_bbox

                # EMA smoothing
                x1 = int(px1 * (1 - self.alpha) + x1 * self.alpha)
                y1 = int(py1 * (1 - self.alpha) + y1 * self.alpha)
                x2 = int(px2 * (1 - self.alpha) + x2 * self.alpha)
                y2 = int(py2 * (1 - self.alpha) + y2 * self.alpha)

                self.prev_bbox = (x1, y1, x2, y2)

        else:
            # اگر safe دیده نشد
            self.missing_frames += 1

            if self.missing_frames > self.max_missing:
                self.prev_bbox = None

        return self.prev_bbox