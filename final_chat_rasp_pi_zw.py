import threading
import network
import sys
import time
import final_my_turtle_rasp_pi_zw as d
import random
"""
This program was created by Elise Beasley, a sophomore at Yorktown High School, and Greg Rusk, a Computer Science
teacher at Yorktown High School.

Based on: network.py  2013 @whaleygeek

A program that creates a communication network between 2 rasp pi zw using an animation make by turtle. Because turtle
does not allow manipulation in a thread other than the main, this program uses a messaging method with queues to
indirectly call and edit turtle. This is an asynchronous input-output program and relies on data from another program
called final_my_turtle_rasp_pi_zw. The user must have 2 rasp pi zw connected to monitors or a way to input into the
terminals and view both screen animations using an application like VNC Viewer. When the user starts the program, they
must input the ip address of the other rasp pi zw, mode - either "first" or "second," and placement of the monitor -
either "left" or "right." Note that the "second" mode must be started BEFORE the "first" mode because it
must wait for input from the "first" mode. The placement of the monitors must be specified to have the ball start at
the correct position and bounce off the correct wall. The initial work for both the first and second modes are done
in their own threads so that the Turtle thread is not manipulated outside of the main loop.
"""


def do_work(data: object) -> None:  # "x y red green blue"
    """
    Collects coordinate data and puts them on the "message box." If the message box is empty, then the function waits
    until it is not. If the message box has a message, then the function collects the new coordinates and color from
    the message box, splits it into x, y, red, green, and blue and sends the new coordinates and color to the other
    rasp pi zw. After this function starts, then the first and second threads close and this function is the main
    thread.
    :param data: an object that is the data from the last position of the turtle in the first rasp pi zw
    :return: None
    """
    # Collect and split the coordinate/color data
    goto_x, goto_y, red, green, blue = data.split()
    # Put a new coordinates/color on the "message box"
    d.request_q.put(f"{goto_x} {goto_y} {red} {green} {blue}")
    print(f"Waiting for coordinates")
    # Wait for a response. If the message box is empty (no coordinates), program sleeps/waits
    while d.response_q.empty():
        time.sleep(.01)
    # Variable "answer" is the new coordinates and color from the response box
    ending_x, ending_y, new_red, new_green, new_blue = d.response_q.get().split()
    print(f"Sending coordinates: {ending_x} {ending_y} {new_red} {new_green} {new_blue}")
    # Tell other rasp pi zw the last position and last color so it can begin continuously
    network.say(f"{ending_x} {ending_y} {new_red} {new_green} {new_blue}")


def do_first_thread(*args: object, **kwargs: object) -> None:
    """
    Starts the first thread and sends the first coordinate data. After the function finishes, this thread ends and
    program continues on the main thread: do_work
    :param args: a special object
    :param kwargs: a special object
    :return: None
    """
    # Send first coordinate and color data
    do_work(kwargs["data"])


def do_second_thread() -> None:
    """
    Waits until it hears a call from the other rasp pi zw. Joins the main thread when finished.
    :return: None
    """
    # Wait until the rasp pi zw hears a call from the first thread
    network.wait(whenHearCall=do_work)


# First argument is the IP address of the other rasp pi zw
# Second argument is the starting mode (first or second)
if len(sys.argv) == 3:
    # Establish ip address and mode
    # sys.argv[0] is the code document that is running
    ip_of_other_rpi = sys.argv[1]
    # Determine which monitor starts the first thread: either "first" or "second"
    mode = sys.argv[2]
    # Determine what side of the desk the first thread will be: either "left" or "right"
    placement = sys.argv[3]
else:
    # This happens if the incorrect number is given or the arguments are wrong
    sys.exit("Bad arguments")

if mode == "first":
    # Hide turtle so that it doesn't start in the middle of the screen
    d.my_turtle.hideturtle()
    # Generate a random color using RGB values between 0 and 255
    start_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # Assign new color
    d.my_turtle.color(start_color)
    # Change the size of the turtle to be a % of original size (orig size is 20px)
    d.my_turtle.shapesize(3)
    # Pick up the pen so that there will not be any trailing draw lines
    d.my_turtle.penup()
    # The amount of which the turtle moves - also affects speed
    d.my_turtle.dy = 2
    d.my_turtle.dx = 2
    # Set gravity so the path is less direct - turtle is "floaty"
    gravity = 0.01
    # Subtract gravity from the change in position
    d.my_turtle.dy -= gravity
    # ----------
    # Generate a random y value that will be the turtle's target height
    random_y = random.randint((-d.max_y_coord) + 60, d.max_y_coord)
    # Set position to be either the positive or negative x maximum depending on their side and a random y value
    # Declare variable to hold the x coordinate, either positive or negative 630.0 in this case
    max_x_coord_decision = 0
    # If the side is "right," then the position should be positive
    if placement == "right":
        d.my_turtle.setpos(d.max_x_coord, random_y)
        max_x_coord_decision = d.max_x_coord
    # If the side is "left," then the position should be negative
    else:
        d.my_turtle.setpos(-d.max_x_coord, random_y)
        max_x_coord_decision = -d.max_x_coord
    # ----------
    # Call the other ip when needed and start do_work
    # Start first thread with the target coordinates and color - sets connection
    network.call(ip_of_other_rpi, whenHearCall=do_work)
    # Assign the function and data arguments to the first thread (before it closes)
    first_thread = threading.Thread(target=do_first_thread, kwargs={"data": f"{max_x_coord_decision} {random_y} "
                                                                            f"{start_color[0]} {start_color[1]} "
                                                                            f"{start_color[2]}"})
    # Do all the Turtle calls BEFORE sending off the first thread because turtle only works in the main loop!
    first_thread.start()

else:
    # Do all the Turtle calls BEFORE sending off the thread because turtle only works in the main loop!
    # Hide turtle so that it doesn't just start in the center of the screen
    d.my_turtle.hideturtle()
    # Assign the function to the second thread (before it joins the main thread)
    second_thread = threading.Thread(target=do_second_thread)
    # Start second thread
    second_thread.start()
    # Thread joins main thread so it is no longer separate
    second_thread.join()

# When the turtle screen is clicked, program exits — inelegant, but ok for now
d.z.exitonclick()
# Start the mainloop for turtle. Note this is in the main thread
d.my_turtle.getscreen().mainloop()
