import turtle as t
import queue as q
import random

"""
Creates and manipulates turtle. Creates message box system for sending coordinates to and from the rasp pi zw.
"""

# Establish turtle
my_turtle = t.Turtle()
# Make screen
screen = my_turtle.getscreen()
# Set the overall window to be 100% of monitor
screen.setup(width=1.0, height=1.0)
# Change the color mode to be RGB instead of the default c mode
screen.colormode(255)
# Set the CANVAS to be the size of the screen (subtract out some border pixels to avoid scrollbar)
screen.screensize(canvwidth=screen.window_width() - 20, canvheight=screen.window_height() - 20)
# Make a variable for the screen so the program ends when the screen is clicked in final_chat_rasp_pu_zw.py
z = t.Screen()
# Decide shape of turtle
my_turtle.shape("circle")
# Change the size of the turtle to be a % of original size (orig size is 20px)
my_turtle.shapesize(3)
# Pick up the pen so that there will not be any trailing draw lines
my_turtle.penup()

# The number of pixels of which the turtle moves - also affects speed
my_turtle.dy = 2
my_turtle.dx = 2
# Set gravity so the path is less direct - turtle is "floaty"
gravity = 0.01

# Positive max x coordinate
max_x_coord = (screen.canvwidth // 2)
# Positive max y coordinate
max_y_coord = (screen.canvheight // 2)

# Request messaging box
request_q = q.Queue()
# Response messaging box
response_q = q.Queue()


def timer_func() -> None:
    """
    Function where turtle is manipulated and messages are sent to the response box.
    :return: None
    """
    # Declare variables to be global for use throughout code
    global tqueue, my_turtle, screen, response_q, request_q
    # Subtract gravity from the change in position
    my_turtle.dy -= gravity

    # Constantly checks if anything is on the queue
    if not request_q.empty():
        # If the message box is not empty, get coordinates and color out
        coordinates = request_q.get()
        # Divide coordinates to be x, y, and the RGB values (red, blue, and green) - splits by " "
        x, y, red, green, blue = coordinates.split()
        # Set position to be the negative last coordinate of the other turtle so that it looks continuous
        my_turtle.setpos(-float(x), float(y))
        # Change color of turtle to be the same color as other turtle for continuity before showing turtle
        my_turtle.color(int(red), int(green), int(blue))
        # Show turtle
        my_turtle.showturtle()
        # ----------
        # Generate a random y value that will be the turtle's target height to bounce off the wall
        random_new_y = float(random.randint((-max_y_coord) + 60, max_y_coord))
        print(f"Moving turtle to {float(x)} {random_new_y} — New color: {red} {green} {blue}")
        # Move turtle to the other side of the screen at a random height (y value)
        my_turtle.goto(float(x), random_new_y)
        # Generate a random color using RGB values between 0 and 255
        new_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # Assign new color
        my_turtle.color(new_color)
        # ----------
        # Generate another random y value that will be the same turtle's target height for moving back to the
        # edge of the screen
        another_random_new_y = float(random.randint((-max_y_coord) + 60, max_y_coord))
        # After turtle reaches position, turtle bounces and goes to the opposite side of the screen to move to the
        # other rasp pi zw with the same x position but a new random y position
        my_turtle.goto(-float(x), another_random_new_y)
        # Hide turtle so that it gives the illusion of going onto the screen of the next turtle
        my_turtle.hideturtle()
        # Put the new coordinates (the next turtle's start position - x will be negated) and color on the response box
        response_q.put(f"{-float(x)} {another_random_new_y} {new_color[0]} {new_color[1]} {new_color[2]}")
    # Updates the screen
    screen.ontimer(timer_func, 5)  # milliseconds


screen.ontimer(timer_func, 5)
