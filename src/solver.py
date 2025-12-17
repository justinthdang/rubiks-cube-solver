import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0" # opens webcam immediately

import cv2
import numpy as np
import kociemba as kc

colour_ranges = {
    # colour : (lower range, upper range, face)
    "white" : ([0, 0, 130], [179, 60, 255], "U"),
    "red" : ([[0, 160], 120, 70], [[10, 179], 255, 255], "R"), # red's hue spans in from the ranges 0-10 and 160-179
    "green" : ([35, 80, 80], [85, 255, 255], "F"),
    "yellow" : ([25, 120, 120], [35, 255, 255], "D"),
    "orange" : ([10, 120, 120], [25, 255, 255], "L"),
    "blue" : ([90, 80, 80], [130, 255, 255], "B")
}

# takes the median of the detected pixels and returns the colour detected
def return_colour(hsv):
    med_hsv = np.median(hsv.reshape(-1, 3), axis = 0).astype(int)
    h, s, v = med_hsv

    for colour, (lower, upper, face) in colour_ranges.items():
        # special case for red's hue wrapping condition
        if colour == "red":
            if ((lower[0][0] <= h <= upper[0][0] or lower[0][1] <= h <= upper[0][1]) and
                lower[1] <= s <= upper[1] and
                lower[2] <= v <= upper[2]):
                return [colour, face]
            
        else:
            if (lower[0] <= h <= upper[0] and
                lower[1] <= s <= upper[1] and
                lower[2] <= v <= upper[2]):
                return [colour, face]
        
    return["-", "-"]
            
def solve_cube(scrambled_state):
    solution = kc.solve(scrambled_state)
    print(solution)
    
def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    scrambled_state = ""

    while True:
        ret, frame = cap.read()
        x, y, z = 490, 210, 100 # top left, bottom left, width/height; increases rightwards and downwards
        face_state = ""

        # draw a 3x3 grid and take them as regions for colour detection
        for i in range(3):
            for j in range(3):
                x1 = x + j * z
                y1 = y + i * z
                x2 = x1 + z
                y2 = y1 + z

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)
                roi = frame[y1 : y2, x1 : x2]
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                colour, face = return_colour(hsv)
                face_state += face
                cv2.putText(frame, colour, (x1 + 5, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.imshow("Full Frame", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("f"):
            scrambled_state += face_state
            print(scrambled_state)

        if key == 27:
            solve_cube(scrambled_state)
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()