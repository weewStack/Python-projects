######################################################################################
# This tutorial is provided by WeeW-Stack
# To get the details of this Tutorial you can take a look on the following link:
# https: // youtu.be/tBgTSdzkSGM
# Enjoy
######################################################################################

from tkinter import *
import serial.tools.list_ports
import threading
import signal
import time

# Dealing with interrupt issue at thread level


def signal_handler(signum, frame):
    sys.exit()


# Dealing with interrupt issue at thread level
signal.signal(signal.SIGINT, signal_handler)


# Class to manage the dynamic animation on the GUI
class Graphics():
    pass

# function that will toggle the Pin


def togglePin():

    if toggle_Pin_btn["text"] in "Pin High":
        print("Pin HIGH")
        pin_on = "1C13\n"
        ser.write(pin_on.encode())
        toggle_Pin_btn["text"] = "Pin Low"

    else:
        print("Pin LOW")
        pin_off = "0C13\n"
        ser.write(pin_off.encode())
        toggle_Pin_btn["text"] = "Pin High"

# function To get / stop the ADC data


def getADC():
    global serialData, graph
    if get_ADC_btn["text"] in "Start ADC":
        get_ADC_btn["text"] = "Stop ADC"
        print("ADC ON")
        pin_on = "AA001\n"
        ser.write(pin_on.encode())
        serialData = True
        t1 = threading.Thread(target=readSerial)
        t1.deamon = True
        t1.start()

    else:
        print("ADC Off")
        serialData = False
        pin_off = "AA000\n"
        ser.write(pin_off.encode())
        get_ADC_btn["text"] = "Start ADC"
        graph.canvas.itemconfig(
            graph.text, text="---")

# Function to initialize the GUI


def connect_menu_init():
    global root, connect_btn, refresh_btn, graph, toggle_Pin_btn, get_ADC_btn
    root = Tk()
    root.title("Serial communication")

    # the size as we have new Gui
    root.geometry("800x600")

    root.config(bg="white")

    port_lable = Label(root, text="Available Port(s): ", bg="white")
    port_lable.grid(column=1, row=2, pady=20, padx=10)

    port_bd = Label(root, text="Baude Rate: ", bg="white")
    port_bd.grid(column=1, row=3, pady=20, padx=10)

    refresh_btn = Button(root, text="R", height=2,
                         width=10, command=update_coms)
    refresh_btn.grid(column=3, row=2)

    connect_btn = Button(root, text="Connect", height=2,
                         width=10, state="disabled", command=connexion)
    connect_btn.grid(column=3, row=4)
    baud_select()
    update_coms()

    graph = Graphics()

    graph.canvas = Canvas(root, width=300, height=300,
                          bg="white", highlightthickness=0)
    graph.canvas.grid(row=6, columnspan=5)

    # part to hide the canvas until needed
    graph.canvas.grid_remove()

    # Dynamic update
    graph.outer = graph.canvas.create_arc(
        10, 10, 290, 290, start=90, extent=100, outline="#f11", fill="#f11", width=2)
    # Static
    graph.canvas.create_oval(
        75, 75, 225, 225, outline="#f11", fill="white", width=2)
    # Dynamic update
    graph.text = graph.canvas.create_text(
        150, 150, anchor=E, font=("Helvetica", "20"), text="---")
    # Static
    graph.canvas.create_text(
        175, 150, anchor=CENTER, font=("Helvetica", "20"), text="mV")

    # Part for the toggle Pin + adding it to global variable
    toggle_Pin_btn = Button(root, text="Pin High", height=2,
                            width=10, command=togglePin)
    toggle_Pin_btn.grid(column=1, row=5)
    toggle_Pin_btn.grid_remove()
    # 1 btn to start / stop reading the ADC data
    get_ADC_btn = Button(root, text="Start ADC", height=2,
                         width=10, command=getADC)
    get_ADC_btn.grid(column=2, row=5)
    get_ADC_btn.grid_remove()


# Function to Enable disable the connect Btn
def connect_check(args):
    if "-" in clicked_com.get() or "-" in clicked_bd.get():
        connect_btn["state"] = "disable"
    else:
        connect_btn["state"] = "active"


# Function to list the Baudes
def baud_select():
    global clicked_bd, drop_bd
    clicked_bd = StringVar()
    bds = ["-",
           "300",
           "600",
           "1200",
           "2400",
           "4800",
           "9600",
           "14400",
           "19200",
           "28800",
           "38400",
           "56000",
           "57600",
           "115200",
           "128000",
           "256000"]
    clicked_bd.set(bds[0])
    drop_bd = OptionMenu(root, clicked_bd, *bds, command=connect_check)
    drop_bd.config(width=20)
    drop_bd.grid(column=2, row=3, padx=50)

# Function to Get the available COMs connected to the PC


def update_coms():
    global clicked_com, drop_COM
    ports = serial.tools.list_ports.comports()
    coms = [com[0] for com in ports]
    coms.insert(0, "-")
    try:
        drop_COM.destroy()
    except:
        pass
    clicked_com = StringVar()
    clicked_com.set(coms[0])
    drop_COM = OptionMenu(root, clicked_com, *coms, command=connect_check)
    drop_COM.config(width=20)
    drop_COM.grid(column=2, row=2, padx=50)
    connect_check(0)

# Function (Thread 3) to Manage the GUI animation


def graph_control(graph):
    graph.canvas.itemconfig(
        graph.outer, exten=int(359*graph.sensor/1000))
    graph.canvas.itemconfig(
        graph.text, text=f"{int(3.3*graph.sensor)}")

# Function (Thread 2) to Manage Reading the UART data from MCU


def readSerial():
    print("thread start")
    global serialData, graph
    average = 0
    sampling = 50
    sample = 0
    while serialData:
        data = ser.readline()
        if len(data) > 0:
            try:
                sensor = int(data.decode('utf8'))
                data_sensor = int(data.decode('utf8'))
                average += data_sensor
                sample += 1
                if sample == sampling:
                    sensor = int(average/sampling)
                    average = 0
                    sample = 0
                # print(sensor)
                    graph.sensor = sensor
                    t2 = threading.Thread(target=graph_control, args=(graph,))
                    t2.deamon = True
                    t2.start()

            except:
                pass

# Function to connect / Disconnect serial Com


def connexion():
    global ser, serialData, toggle_Pin_btn
    if connect_btn["text"] in "Disconnect":
        connect_btn["text"] = "Connect"
        refresh_btn["state"] = "active"
        drop_bd["state"] = "active"
        drop_COM["state"] = "active"
        toggle_Pin_btn.grid_remove()
        # 3 Hide the ADC widgets
        graph.canvas.grid_remove()
        get_ADC_btn.grid_remove()

    else:
        connect_btn["text"] = "Disconnect"
        refresh_btn["state"] = "disable"
        drop_bd["state"] = "disable"
        drop_COM["state"] = "disable"
        port = clicked_com.get()
        baud = clicked_bd.get()
        # Hide the btn when the connection ends
        try:
            ser = serial.Serial(port, baud, timeout=0)
        except:
            pass
        # Show the toggle Pin and comment The serial read + Remove
        toggle_Pin_btn.grid()
        # 2 Show the adc widget
        graph.canvas.grid()
        get_ADC_btn.grid()

# Dealing with interrupt issue at thread level


def close_window():
    global root, serialData
    serialData = False
    time.sleep(0.25)
    root.destroy()


connect_menu_init()  # Start the GUI & Initialization
root.protocol("WM_DELETE_WINDOW", close_window)  # When Closing the Window
root.mainloop()  # Stating the main loop / Thread
