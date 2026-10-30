import cv2
import mediapipe as mp
import random
import time
import pyttsx3

# Voice setup
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Levels
easy = [("2+2",4), ("1+3",4), ("2+3",5)]
medium = [("5-2",3), ("6-3",3), ("4+2",6)]
hard = [("3+4",7), ("8-3",5), ("6+2",8)]

level = easy
score = 0
total_questions = 5

q, ans = random.choice(level)
speak("Game started")

def count_fingers(hand_landmarks):
    tips = [4,8,12,16,20]
    fingers = []

    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

question_count = 0
start_time = time.time()

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    total_fingers = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            total_fingers = count_fingers(handLms)

    # Display
    cv2.putText(img, f"Q: {q}", (10,50),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    cv2.putText(img, f"Ans: {total_fingers}", (10,100),
                cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)

    cv2.putText(img, f"Score: {score}", (10,150),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)

    # Check answer
    if total_fingers == ans:
        speak("Correct")
        score += 1
        question_count += 1
        time.sleep(1)

        # Level change
        if score >= 3:
            level = medium
        if score >= 6:
            level = hard

        if question_count >= total_questions:
            break

        q, ans = random.choice(level)
        speak(f"Next question {q}")

    cv2.imshow("Smart Game", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Game Over Screen
cap.release()
cv2.destroyAllWindows()

print("Game Over!")
print("Your Score:", score)

if score >= 4:
    speak("Great job!")
else:
    speak("Try again")