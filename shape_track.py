import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

canvas = None
points = []
prev_x, prev_y = 0, 0
start_point = None

smoothening = 7
mode_text = "IDLE"

cap = cv2.VideoCapture(0)


def detect_shape(points, canvas):
    try:
        if len(points) < 25:
            return

        pts = np.array(points, dtype=np.int32)

        h, w, _ = canvas.shape
        img = np.zeros((h, w), dtype=np.uint8)

        cv2.polylines(img, [pts], True, 255, 10)
        img = cv2.GaussianBlur(img, (5, 5), 0)

        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue

            peri = cv2.arcLength(cnt, True)
            if peri == 0:
                continue

            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            sides = len(approx)

            x, y, w, h = cv2.boundingRect(cnt)
            circularity = 4 * np.pi * (area / (peri * peri))

            cv2.drawContours(canvas, [cnt], -1, (0, 0, 0), thickness=cv2.FILLED)

            color = (0, 255, 0)

            if circularity > 0.8:
                shape = "Circle"
                (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                cv2.circle(canvas, (int(cx), int(cy)), int(radius), color, 3)

            elif sides == 3:
                shape = "Triangle"
                cv2.drawContours(canvas, [approx], 0, color, 3)

            elif sides == 4:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int32(box)

                rw, rh = rect[1]
                if rh == 0:
                    continue

                ratio = rw / rh
                shape = "Square" if 0.9 <= ratio <= 1.1 else "Rectangle"

                cv2.drawContours(canvas, [box], 0, color, 3)

            elif sides == 5:
                shape = "Pentagon"
                cv2.drawContours(canvas, [approx], 0, color, 3)

            elif sides == 6:
                shape = "Hexagon"
                cv2.drawContours(canvas, [approx], 0, color, 3)

            else:
                shape = "Polygon"
                cv2.drawContours(canvas, [approx], 0, color, 3)

            cv2.putText(canvas, shape, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    except Exception as e:
        print("Shape error:", e)


while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.flip(img, 1)

    if canvas is None:
        canvas = np.zeros_like(img)

    mode_text = "IDLE"

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:

            h, w, _ = img.shape

            x = int(handLms.landmark[8].x * w)
            y = int(handLms.landmark[8].y * h)

            cv2.circle(img, (x, y), 8, (0, 255, 255), -1)

            index_up = handLms.landmark[8].y < handLms.landmark[6].y
            middle_up = handLms.landmark[12].y < handLms.landmark[10].y
            ring_up = handLms.landmark[16].y < handLms.landmark[14].y
            pinky_up = handLms.landmark[20].y < handLms.landmark[18].y
            thumb_up = handLms.landmark[4].x < handLms.landmark[3].x

            fingers = sum([thumb_up, index_up, middle_up, ring_up, pinky_up])

            if fingers == 5:
                canvas[:] = 0
                points = []
                prev_x, prev_y = 0, 0
                start_point = None
                mode_text = "CLEAR"

            elif fingers == 3:
                prev_x, prev_y = 0, 0
                start_point = None
                cv2.circle(canvas, (x, y), 35, (0, 0, 0), -1)
                mode_text = "ERASE"

            elif fingers == 2:
                if start_point is None:
                    start_point = (x, y)
                else:
                    cv2.circle(canvas, start_point, 20, (0, 0, 0), -1)
                    cv2.circle(canvas, (x, y), 20, (0, 0, 0), -1)
                    cv2.line(canvas, start_point, (x, y), (0, 255, 0), 5)
                    start_point = None

                prev_x, prev_y = 0, 0
                mode_text = "LINE"

            elif fingers == 1 and index_up:
                points.append((x, y))

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = x, y

                curr_x = prev_x + (x - prev_x) // smoothening
                curr_y = prev_y + (y - prev_y) // smoothening

                cv2.line(canvas, (prev_x, prev_y), (curr_x, curr_y), (0, 255, 0), 5)

                prev_x, prev_y = curr_x, curr_y
                mode_text = "DRAW"

            else:
                if len(points) > 25:
                    detect_shape(points, canvas)
                    points = []

                prev_x, prev_y = 0, 0
                start_point = None
                mode_text = "SHAPE"

    # -------- DISPLAY --------
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, inv)
    img = cv2.bitwise_or(img, canvas)

    # 🔥 SMALL MODE TEXT (ONLY CHANGE)
    cv2.rectangle(img, (0, 0), (180, 30), (0, 0, 0), -1)

    cv2.putText(img, mode_text, (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("AI Gesture Draw", img)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()



