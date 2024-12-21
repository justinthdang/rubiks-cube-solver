import numpy as np
import cv2

# turn on webcam
cap=cv2.VideoCapture(0)
def nothing(x):
    pass

# create trackbars for lower and upper hsv values
cv2.namedWindow("Trackbars")
cv2.createTrackbar("Lower H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("Lower S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Lower V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Upper H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("Upper S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("Upper V", "Trackbars", 255, 255, nothing)

# webcam running
while True:
    ret,frame = cap.read()
    frame = cv2.resize(frame, (1024, 768))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# get trackbar positions
    lower_h = cv2.getTrackbarPos("Lower H", "Trackbars")
    lower_s = cv2.getTrackbarPos("Lower S", "Trackbars")
    lower_v = cv2.getTrackbarPos("Lower V", "Trackbars")
    upper_h = cv2.getTrackbarPos("Upper H", "Trackbars")
    upper_s = cv2.getTrackbarPos("Upper S", "Trackbars")
    upper_v = cv2.getTrackbarPos("Upper V", "Trackbars")
# group lower and upper hsv values into arrays
    lower = np.array([lower_h, lower_s, lower_v])
    upper = np.array([upper_h, upper_s, upper_v])
# create mask for hsv values that fall within specified range
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask = mask)    
    cv2.imshow("result", result)
# "q" ends program
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# turn off webcam
cap.release()
cv2.destroyAllWindows()