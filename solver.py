import cv2
import numpy as np
import kociemba as kc
import serial

s = serial.Serial("COM4", 9600)

# hsv colour ranges
colour_ranges = {
    #               lower            upper
    "white"  : ([0, 0, 173],    [179, 99, 241]),
    "yellow" : ([19, 137, 179], [44, 234, 255]),
    "green"  : ([51, 121, 153], [75, 203, 255]),
    "blue"   : ([85, 132, 153], [110, 255, 246]),
    "red"    : ([0, 149, 187],  [7, 212, 241]),
    "orange" : ([10, 170, 210],  [19, 239, 255]),
}

# convert colour to corresponding face
def colour_to_face(colour):
    if colour == "white":
        return "U"
    elif colour == "yellow":
        return "D"
    elif colour == "green":
        return "F"
    elif colour == "blue":
        return "B"
    elif colour == "red":
        return "R"
    elif colour == "orange":
        return "L"

# returns the corresponding colour that falls between the colour ranges
def detect_colour(hsv_value):
    for colour, (lower, upper) in colour_ranges.items():
        if all(lower[i] <= hsv_value[i] <= upper[i] for i in range(3)):
            return colour

# draws 9 squares from top-left to bottom-right, creating a 3x3 grid
def grid(frame, colour, thickness):
    x_og, y_og = 362, 234
    face_colours = []
    for y in range(3):
        x_start, y_start = x_og, y_og + y * 100
        for x in range(3):
            x_end, y_end = x_start + 100, y_start + 100
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), colour, thickness)
# detect center 40% of square to avoid noise
            offset_x_start, offset_y_start = x_start + 30, y_start + 30
            offset_x_end, offset_y_end = x_end - 30, y_end - 30
# detects the colour in the roi and adds to list
            roi = frame[offset_y_start:offset_y_end, offset_x_start:offset_x_end]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            avg_hsv = np.mean(hsv_roi, axis=(0, 1)).astype(int)
            detected_colour = detect_colour(avg_hsv)
            face_colours.append(detected_colour)
# places text of colour in grid
            text_x, text_y = x_start + 10, y_start + 30
            cv2.putText(frame, detected_colour, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            x_start += 100
    return face_colours

# find solution
def find_solution(faces):
    converted = ""
    for face in faces:
        for colour in face:
            converted += colour_to_face(colour)
    solution = kc.solve(converted)
    print(solution)

# turn on webcam
cap = cv2.VideoCapture(0)
faces = []

# webcam running
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1024, 768))
    key = cv2.waitKey(1) & 0XFF
# calls function to detect colours of each sticker
    current_face = grid(frame, (255, 255, 255), 5)
    cv2.imshow('Detect Faces', frame)
# "f" captures current face and adds it to list
    if key == ord("f"):
        faces.append(current_face)
        print("Face detected")
# "q" converts list to string, shows solution and ends program
    elif key == ord("q"):
        find_solution(faces)
        break

# turn off webcam
cap.release()
cv2.destroyAllWindows()

'''
    kociemba library follows this order when capturing faces
    U = white
    R = red
    F = green
    D = yellow
    L = orange
    B = blue
'''