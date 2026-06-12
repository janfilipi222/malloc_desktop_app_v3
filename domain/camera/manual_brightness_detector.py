import cv2
import numpy as np

class ManualBrightnessDetector:
    def __init__(
        self,
        threshold=190,
        min_area=300,
        max_area=50000,
        blur=7,
        aspect_range=(0.7, 1.3)
    ):
        self.threshold = threshold
        self.min_area = min_area
        self.max_area = max_area
        self.blur = blur
        self.aspect_range = aspect_range

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # odšumění
        gray = cv2.GaussianBlur(gray, (self.blur, self.blur), 0)

        # FIXNÍ threshold (ruční kontrola)
        _, mask = cv2.threshold(
            gray,
            self.threshold,
            255,
            cv2.THRESH_BINARY
        )

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        output = frame.copy()

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area < self.min_area or area > self.max_area:
                continue

            rect = cv2.minAreaRect(cnt)
            (cx, cy), (w, h), angle = rect

            if w == 0 or h == 0:
                continue

            aspect = w / h
            if not (self.aspect_range[0] <= aspect <= self.aspect_range[1]):
                continue

            box = cv2.boxPoints(rect)
            box = np.int32(box)

            results.append({
                "x": cx,
                "y": cy,
                "w": w,
                "h": h,
                "angle": angle,
                "area": area
            })

            cv2.drawContours(output, [box], 0, (0, 255, 0), 2)
            cv2.circle(output, (int(cx), int(cy)), 3, (255, 0, 0), -1)

        return results, mask, output