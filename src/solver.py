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
        solution = kc.solve(converted)
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
    
class ControlCube():
    # initialize serial communication
    def __init__(self, port, baud_rate):
        self.s = serial.Serial(port, baud_rate)
    # sends command to move stepper
    def stepper_command(self, steps):
        self.s.write(b"A")
        self.s.write(str(steps).encode("utf-8"))
        self.s.flush()
    # sends command to move servo
    def servo_command(self, angle):
        self.s.write(b"B")
        self.s.write(str(angle).encode("utf-8"))
        self.s.flush()
    # send command to simulate key press "f"
    def key_command_f(self):
        self.s.write(b"C")
        self.s.flush()
    # send command to simulate key press "q"
    def key_command_q(self):
        self.s.write(b"D")
        self.s.flush()
    # rotate cube/face 90 degrees clockwise
    def rotate_90_cw(self):
        self.stepper_command(512)
    # rotate cube/face 90 degrees counterclockwise
    def rotate_90_ccw(self):
        self.stepper_command(-512)
    # rotate cube/face 180 degrees
    def rotate_180(self):
        self.stepper_command(1024)
    # flips cube
    def flip(self):
        self.servo_command(30)
        self.servo_command(-30)
    # grabs top of cube
    def grab(self):
        self.servo_command(60)
    # ungrabs top of cube
    def ungrab(self):
        self.servo_command(-60)
    # scans face
    def scan(self):
        self.key_command_f()
    # starts solve
    def start(self):
        self.key_command_q()

class SolveCube:
    def __init__(self, control_cube, solution):
        self.control_cube = control_cube
        self.solution = solution
    # initial scanning of all faces
    def scan_faces(self):
        # scan U face and set up for R face
        self.control_cube.scan()
        self.control_cube.rotate_180()
        self.control_cube.flip()
        self.control_cube.rotate_90_ccw()
        # scan R face and set up for F face
        self.control_cube.scan()
        self.control_cube.rotate_90_ccw()
        # scan F face and set up for D face
        self.control_cube.scan()
        self.control_cube.rotate_180()
        self.control_cube.flip()
        self.control_cube.rotate_180()
        # scan D face and set up for L face
        self.control_cube.scan()
        self.control_cube.flip()
        self.control_cube.rotate_90_ccw()
        # scan L face and set up for B face
        self.control_cube.scan()
        self.control_cube.rotate_90_ccw()
        # scan B face and start solve => U face is home (bottom) face
        self.control_cube.scan()
        self.control_cube.start()
    # optimal moves to get from the U face to another face
    def setup_moves(self, move):
        if move[0] == "D":
            self.control_cube.flip()
            self.control_cube.flip()
        elif move[0] == "B":
            self.control_cube.flip()
        elif move[0] == "F":
            self.control_cube.rotate_180()
            self.control_cube.flip()
        elif move[0] == "R":
            self.control_cube.rotate_90_cw()
            self.control_cube.flip()
        elif move[0] == "L":
            self.control_cube.rotate_90_ccw()
            self.control_cube.flip()
        # if U face then do nothing
        else:
            pass
    # turn face
    def turn_face(self, move):
        if move[1] == "'":
            self.control_cube.grab()
            self.control_cube.rotate_90_ccw()
            self.control_cube.ungrab()
        elif move[1] == "2":
            self.control_cube.grab()
            self.control_cube.rotate_180()
            self.control_cube.ungrab()
        else:
            self.control_cube.grab()
            self.control_cube.rotate_90_cw()
            self.control_cube.ungrab()
    # remap faces about U
    def remap_faces(self, moves):
        string_moves = " ".join(moves)
        if string_moves[0] == "D":
            # U <=> D, F <=> B
            string_moves = string_moves.replace("U", "T").replace("D", "U").replace("T", "D")
            string_moves = string_moves.replace("F", "T").replace("B", "F").replace("T", "B")
            new_moves = string_moves.split(" ")
            return new_moves
        elif string_moves[0] == "B":
            # U => F => D => B => U
            string_moves = string_moves.replace("U", "T").replace("F", "U").replace("D", "F").replace("B", "D").replace("T", "B")
            new_moves = string_moves.split(" ")
            return new_moves
        elif string_moves[0] == "F":
            # R <=> L, U => B => D => F => U
            string_moves = string_moves.replace("R", "T").replace("L", "R").replace("T", "L")
            string_moves = string_moves.replace("U", "T").replace("B", "U").replace("D", "B").replace("F", "D").replace("T", "F")
            new_moves = string_moves.split(" ")
            return new_moves
        elif string_moves[0] == "R":
            # U => R => F => U, D => L => B => D
            string_moves = string_moves.replace("U", "T").replace("R", "U").replace("F", "R").replace("T", "F")
            string_moves = string_moves.replace("D", "T").replace("L", "D").replace("B", "L").replace("T", "B")
            new_moves = string_moves.split(" ")
            return new_moves
        elif string_moves[0] == "L":
            # U => L => F => U, D => R => B => D
            string_moves = string_moves.replace("U", "T").replace("L", "U").replace("F", "L").replace("T", "F")
            string_moves = string_moves.replace("D", "T").replace("R", "D").replace("B", "R").replace("T", "B")
            new_moves = string_moves.split(" ")
            return new_moves
        else:
            # if U face then do nothing
            new_moves = string_moves.split(" ")
            return new_moves
# iterate through list of moves in solution
    def iterate(self):
        moves = self.solution.split(" ")
        while moves:
            move = moves[0]
            self.setup_moves(move)
            self.turn_face(move)
            moves = self.remap_faces(moves)
            moves.pop(0)

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
            solve_cube = SolveCube(control_cube, solution)
            solve_cube.iterate()
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