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

screen = curses.initscr()


row = 0
col = 0
screen.addstr(row, col, "Data: ")
screen.addstr(row+3, col, "Insert q to quite the program ")
screen.refresh()


def my_Serial():
    global uart
    port = "COM3"
    ser = serial.Serial(port, 115200, timeout=0)
    average = 0
    sampling = 200
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
                    screen.addstr(row, 8, '      mV')
                    screen.addstr(row, 8, f'{int(sensor*3.3)}')
                    screen.addstr(1, 0, '')
                    screen.refresh()
            except:
                pass

        # print(data_sensor)


def signal_handler(signum, frame):
    sys.exit()


signal.signal(signal.SIGINT, signal_handler)

t1 = threading.Thread(target=my_Serial)
t1.daemon = True
t1.start()

while True:
    key = screen.getkey()
    if key == 'q':
        uart = False
        break
