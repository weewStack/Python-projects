# Python library Requirements:
# pip install pyserial
# pip install windows-curses

# input for "Value"+ "Newline"


import serial
import curses
import threading
import signal
import sys

global uart
uart = True
row = 0
col = 0

# Initialize the curses library


def curses_init():
    global screen
    screen = curses.initscr()
    screen.addstr(row, col, "Data: ")
    screen.addstr(row+3, col, "Insert q to quite the program ")
    screen.refresh()
    curses.start_color()
    curses.use_default_colors()
    for i in range(40, 140):
        curses.init_color(i, 255, i*3, 255-i)
        curses.init_pair(i + 1, 0, i+1)

# Initialize The thread that will run into the background


def my_Serial():
    global uart, screen
    port = "COM3"
    ser = serial.Serial(port, 115200, timeout=0)
    average = 0
    sampling = 50
    sample = 0

    while uart:
        data = ser.readline()
        if len(data) > 0:
            try:
                data_sensor = int(data.decode('utf8'))
                average += data_sensor
                sample += 1
                if sample == sampling:
                    sensor = int(average/sampling)
                    average = 0
                    sample = 0
                    empty_bar = " "*110
                    screen.addstr(row, 8, '     mV, ')
                    screen.addstr(
                        row, 8, f'{int(sensor*3.3)}')
                    screen.addstr(row, 17, '   %')
                    screen.addstr(
                        row, 17, f'{int(sensor/ 10)}')
                    screen.addstr(1, 0, '')
                    screen.addstr(1, 0, empty_bar)
                    for i in range(int(sensor/10)):
                        screen.addstr(1, i, " ", curses.color_pair(i+40))
                    screen.addstr(1, 0, '')
                    screen.refresh()
            except:
                pass

        # print(data_sensor)

# Running the Thread


def serial_thread():
    t1 = threading.Thread(target=my_Serial)
    t1.daemon = True
    t1.start()

# Handling the Interrupt


def signal_handler(signum, frame):
    sys.exit()

# Main thread and user interraction


def main_thread():
    global uart, screen
    while True:
        key = screen.getkey()
        if key == 'q':
            uart = False
            # screen.addstr(3, 0, 'HHHHHH', curses.color_pair(254))
            break


# Managing the Interrupt
signal.signal(signal.SIGINT, signal_handler)

# Main program
curses_init()    # Initializing the the curses lib
serial_thread()  # Running the the Secondary thread
main_thread()  # Running the Main thread
