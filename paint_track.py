import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from google import genai
from PIL import Image

client = genai.Client(api_key="AIzaSyDZKJSi_ziH036PGYBhUghdZHI0wKqs5I0")



try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1080)
    cap.set(4, 720)
except Exception as e:
    print("Camera Init Error:", e)

try:
    detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1,
                            detectionCon=0.7, minTrackCon=0.5)
except Exception as e:
    print("Detector Init Error:", e)

prev_pos = None
canvas = None
image_combined = None
ai_answer = "Waiting for input..."

def getHandInfo(hands):
    try:
        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            fingers = detector.fingersUp(hand)
            return fingers, lmList
        return None
    except Exception as e:
        print("getHandInfo Error:", e)
        return None

def draw(info, prev_pos, canvas, img):
    try:
        fingers, lmList = info
        current_pos = None
        if fingers == [0, 1, 0, 0, 0]:
            current_pos = lmList[8][0:2]
            if prev_pos is None:
                prev_pos = current_pos
            cv2.line(canvas, current_pos, prev_pos, (243, 75, 69), 10)
        elif fingers == [1, 1, 1, 1, 1]:
            canvas = np.zeros_like(img)
        return current_pos, canvas
    except Exception as e:
        print("Draw Error:", e)
        return prev_pos, canvas

def sendtoAI(canvas, fingers):
    try:
        if fingers == [0, 1, 0, 0, 1]:
            img_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "solve this math problem (quant, trigonometry, algebra, derivative) "
                    "and if that is not applicable, solve it by your choice:",
                    pil_img
                ],
            )
            return response.text
        return None
    except Exception as e:
        print("AI Error:", e)
        return None

while True:
    try:
        success, img = cap.read()
        if not success:
            print("Frame Read Error")
            break

        img = cv2.flip(img, 1)

        try:
            hands, img = detector.findHands(img, draw=False, flipType=True)
        except Exception as e:
            print("findHands Error:", e)
            hands = []

        if canvas is None:
            canvas = np.zeros_like(img)

        info = getHandInfo(hands)

        if info:
            fingers, lmList = info
            prev_pos, canvas = draw(info, prev_pos, canvas, img)

            image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)

            result = sendtoAI(canvas, fingers)
            if result:
                ai_answer = result
        else:
            image_combined = img

        # 🔥 SHOW OUTPUT
        cv2.putText(image_combined, ai_answer, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("PixelSense AI Board", image_combined)

        # press q to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print("Main Loop Error:", e)

cap.release()
cv2.destroyAllWindows()