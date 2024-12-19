import cv2
import numpy as np
import kociemba as kc

# hsv colour ranges
colour_ranges = {
    #               lower            upper
    "white"  : ([0, 0, 156],    [179, 101, 243]),
    "yellow" : ([19, 121, 175], [39, 255, 255]),
    "green"  : ([55, 137, 142], [75, 203, 255]),
    "blue"   : ([97, 203, 146], [112, 255, 255]),
    "red"    : ([0, 114, 118],  [7, 255, 255]),
    "orange" : ([9, 160, 206],  [19, 255, 255]),
}

# returns the corresopnding colour that falls between the colour ranges
def detect_colour(hsv_value):
    for colour, (lower, upper) in colour_ranges.items():
        if all(lower[i] <= hsv_value[i] <= upper[i] for i in range(3)):
            return colour

# draws grid and detects colours in each square
def grid(frame, colour, thickness):
    x_og, y_og = 362, 234

    # loops to draw each square
    for y in range(3):
        x_start, y_start = x_og, y_og + y * 100
        for x in range(3):
            x_end, y_end = x_start + 100, y_start + 100
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), colour, thickness)

            # detects the colour in the roi
            roi = frame[y_start:y_end, x_start:x_end]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            avg_hsv = np.mean(hsv_roi, axis=(0, 1)).astype(int)
            detected_colour = detect_colour(avg_hsv)

            # places text of colour in grid
            text_x, text_y = x_start + 10, y_start + 30
            cv2.putText(frame, detected_colour, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            x_start += 100
        
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1024, 768))

    grid(frame, (255, 255, 255), 5)
    cv2.imshow('Detect Faces', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

'''
    U = white
    R = red
    F = green
    D = yellow
    L = orange
    B = blue
'''