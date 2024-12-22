# import libraries
import cv2
import numpy as np
import kociemba as kc
import serial

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

class Cube:
# initialize list of faces
    def __init__(self):
        self.faces = []
# add face to list
    def add_face(self, face):
        self.faces.append(face)
# find solution
    def find_solution(self):
        converted = ""
        for face in self.faces:
            for colour in face:
                converted += colour_to_face(colour)
        solution = kc.solve(converted).split(" ")
        return(solution)

class VisionSystem:
# call colour ranges
    def __init__(self, colour_ranges):
        self.colour_ranges = colour_ranges
# returns the corresponding colour that falls between the colour ranges
    def detect_colour(self, hsv_value):
        for colour, (lower, upper) in self.colour_ranges.items():
            if all(lower[i] <= hsv_value[i] <= upper[i] for i in range(3)):
                return colour
# draws 9 squares from top-left to bottom-right, creating a 3x3 grid
    def grid(self, frame, colour, thickness):
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
                detected_colour = self.detect_colour(avg_hsv)
                face_colours.append(detected_colour)
# places text of colour in grid
                text_x, text_y = x_start + 10, y_start + 30
                cv2.putText(frame, detected_colour, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                x_start += 100
        return face_colours
    
def ControlCube():
# initialize serial communication
    def __init__(self, port, baud_rate):
        self.s = serial.Serial(port, baud_rate)
# sends command to move stepper
    def stepper_command(self, steps):
        self.s.write(b"S")
        self.s.write(str(steps).encode("utf-8"))
        self.s.flush()
# sends command to move servo
    def servo_command(self, angle):
        self.s.write(b"F")
        self.s.write(str(angle).encode("utf-8"))
        self.s.flush()
# send command to simulate key press
    def key_command(self):
        self.s.write(b"K")
        self.s.flush()

def main():
# initialize objects and webcam
    cube = Cube()
    vision_system = VisionSystem(colour_ranges)
    control_cube = ControlCube("COM4", 9600)
    cap = cv2.VideoCapture(0)
# run webcam
    while cap.isOpened():
# initialize frame for reading and key press
        ret, frame = cap.read()
        frame = cv2.resize(frame, (1024, 768))
        key = cv2.waitKey(1) & 0xFF
# calls object and its method to detect colour of each sticker
        current_face = vision_system.grid(frame, (255, 255, 255), 5)
        cv2.imshow('Detect Faces', frame)
# "f" captures current face and adds it to list
        if key == ord("f"):
            cube.add_face(current_face)
            print("Face detected")
# "q" converts list to string, shows solution and ends program
        elif key == ord("q"):
            solution = cube.find_solution()
            print(solution)
            break
# turn off and close webcam
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

'''
    kociemba library follows this order when capturing faces
    U = white
    R = red
    F = green
    D = yellow
    L = orange
    B = blue
'''