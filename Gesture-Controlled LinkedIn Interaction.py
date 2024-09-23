import cv2
import mediapipe as mp
import time
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to recognize gestures
def recognize_gesture(landmarks, handedness):
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]
    ring_tip = landmarks[16]
    ring_pip = landmarks[14]
    pinky_tip = landmarks[20]
    pinky_pip = landmarks[18]

    thumb_up = thumb_tip.y < thumb_ip.y < thumb_mcp.y
    index_down = index_tip.y > index_pip.y
    middle_down = middle_tip.y > middle_pip.y
    ring_down = ring_tip.y > ring_pip.y
    pinky_down = pinky_tip.y > pinky_pip.y

    if thumb_up and index_down and middle_down and ring_down and pinky_down:
        return "إعجاب"
    
    mcp_y_avg = (landmarks[5].y + landmarks[9].y + landmarks[13].y + landmarks[17].y) / 4

    if mcp_y_avg < 0.5:
        if handedness == "Right" and not (thumb_up and index_down and middle_down and ring_down and pinky_down):
            return "next"
        elif handedness == "Left" and not (thumb_up and index_down and middle_down and ring_down and pinky_down):
            return "prev"
    return "none"

# تعديل الوظيفة للعثور على الأزرار باستخدام XPaths مباشرة
def perform_linkedin_action(driver, gesture):
    if gesture == "إعجاب":
        try:
            if gesture == "إعجاب":
                like_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='ember512']/span/div/span"))
                )
                like_button.click()
                print("Like button clicked")
        except Exception as e:
            print(f"Error performing like action: {e}")


# Selenium setup
chrome_options = Options()
chrome_options.add_argument(r"C:\Users\Lenovo\AppData\Local\Google\Chrome\User Data")  # Replace with your Chrome user data path
chrome_service = Service("D:/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")  # Path to ChromeDriver

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

linkedin_url = "https://www.linkedin.com/in/mohamed2mohsen/recent-activity/all/"  # Replace with your LinkedIn profile URL
driver.get(linkedin_url)

# Wait for the page to load
time.sleep(2)

# State variables
liked_state = False
scroll_timestamp = time.time()

def scroll_faster(driver, direction, scrolls=1):
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(scrolls):
        if direction == "down":
            body.send_keys(Keys.PAGE_DOWN)
        elif direction == "up":
            body.send_keys(Keys.PAGE_UP)
        time.sleep(0.1)

# Start capturing video from webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            handedness = hand_handedness.classification[0].label
            gesture = recognize_gesture(landmarks, handedness)

            print(f"Hand: {handedness}, Gesture: {gesture}")

            if not liked_state and (time.time() - scroll_timestamp > 1):
                if gesture == "next":
                    print("Next gesture detected - Scrolling down")
                    scroll_faster(driver, "down", scrolls=1)
                    scroll_timestamp = time.time()

                elif gesture == "prev":
                    print("Previous gesture detected - Scrolling up")
                    scroll_faster(driver, "up", scrolls=1)
                    scroll_timestamp = time.time()

            if gesture != "none":
                perform_linkedin_action(driver, gesture)

    cv2.imshow("Hand Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
driver.quit()
