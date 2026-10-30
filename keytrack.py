import cv2
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
import time


DETECTION_CONFIDENCE = 0.7
CLICK_DISTANCE = 30
CLICK_DELAY = 0.30
SMOOTHING = 0.3


keyboard = Controller()
finaltext = ""

cap = cv2.VideoCapture(0)
cap.set(3, 1080)  
cap.set(4, 720)

detector = HandDetector(detectionCon=DETECTION_CONFIDENCE)

prev_click_time = 0
smooth_x, smooth_y = 0, 0


class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


def drawall(img, buttonlist):
    for button in buttonlist:
        x, y = button.pos
        w, h = button.size

        cv2.rectangle(img, button.pos, (x+w, y+h), (171,57,57,), cv2.FILLED)
        cv2.putText(img, button.text, (x+25, y+60),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
    return img


keys = [["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L",";"],
        ["Z","X","C","V","B","N","M",",",".","/"]]

buttonlist = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonlist.append(Button([90*j+50, 90*i+50], key))


while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img)
    img = drawall(img, buttonlist)

    if hands:
        lmList = hands[0]['lmList']

       
        raw_x, raw_y = lmList[8][0], lmList[8][1]
        smooth_x = int(SMOOTHING * raw_x + (1-SMOOTHING) * smooth_x)
        smooth_y = int(SMOOTHING * raw_y + (1-SMOOTHING) * smooth_y)

        x_finger, y_finger = smooth_x, smooth_y

        # Draw pointer dot
        cv2.circle(img, (x_finger, y_finger), 10, (0,255,255), cv2.FILLED)

        # -------- Button Interaction --------
        for button in buttonlist:
            x, y = button.pos
            w, h = button.size

            if x < x_finger < x+w and y < y_finger < y+h:
                cv2.rectangle(img, button.pos, (x+w, y+h), (175,0,175), cv2.FILLED)
                cv2.putText(img, button.text, (x+25, y+60),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)

                # -------- Click Detection --------
                length, info, _ = detector.findDistance(
                    lmList[8][:2], lmList[12][:2], img)

                current_time = time.time()

                if length < CLICK_DISTANCE and (current_time - prev_click_time) > CLICK_DELAY:
                    keyboard.press(button.text)
                    finaltext += button.text
                    prev_click_time = current_time

                    cv2.rectangle(img, button.pos, (x+w, y+h), (0,255,0), cv2.FILLED)

    # -------- Display Typed Text --------
    cv2.rectangle(img,(50,350), (850,450), (175,0,175), cv2.FILLED)
    cv2.putText(img, finaltext, (60,420),
                cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)

    # -------- Show Window --------
    cv2.imshow("AI Virtual Keyboard", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ----------------
cap.release()
cv2.destroyAllWindows()
