######################################################################################
# This tutorial is provided by WeeW-Stack
# To get the details of this Tutorial you can take a look on the following link:
# https:
# Enjoy
######################################################################################

from tkinter import *
import serial.tools.list_ports  # pip install pyserial
import threading
import signal
import time
# 1 The Library above will add the plot to the plot function (Graphs) to Tkinter Gui
import matplotlib.pyplot as plt  # pip install matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


def signal_handler(signum, frame):
    # Dealing with interrupt issue at thread level
    sys.exit()


# Dealing with interrupt issue at thread level
signal.signal(signal.SIGINT, signal_handler)


class Graphics():
    # Class to manage the dynamic animation on the GUI
    pass


def togglePin():
    # function that will toggle the Pin
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


def getADC():
    #############################################
    # function To get / stop the ADC data
    #############################################
    global serialData, graph, refTime
    if get_ADC_btn["text"] in "Start ADC":

        ########################################################
        # 4: Show the hidden plot widget & Risze the Gui
        graph.canvas.grid()
        chart.get_tk_widget().grid()
        root.geometry("1200x500")
        #########################################################
        #######################################
        # 5 : Initialize the timer for chart reader
        if len(xData) == 0:
            refTime = time.perf_counter()
        else:
            refTime = time.perf_counter()-xData[len(xData)-1]
        #######################################

        get_ADC_btn["text"] = "Stop ADC"
        print("ADC ON")
        pin_on = "AA001\n"
        ser.write(pin_on.encode())
        serialData = True
        t1 = threading.Thread(target=readSerial)
        t1.deamon = True
        t1.start()
        #######################################
        # 6: Start to update the graph plot
        update_chart()
        #######################################

    else:
        ############################################################
        # 4: Show the hidden plot widget & Update the Root size
        root.geometry("500x300")
        graph.canvas.grid_remove()
        chart.get_tk_widget().grid_remove()
        #############################################################
        print("ADC Off")
        serialData = False
        pin_off = "AA000\n"
        ser.write(pin_off.encode())
        get_ADC_btn["text"] = "Start ADC"
        graph.canvas.itemconfig(
            graph.text, text="---")


def update_chart():
    ###########################################
    # 7: Function That update the graph
    ###########################################
    global x, y,  fig,  chart, ax, serialData, xData, yData
    ax.clear()
    ax.plot(x, y, '-', dash_capstyle='projecting')
    ax.grid(color='b', linestyle='-', linewidth=0.2)
    fig.canvas.draw()
    if serialData:
        root.after(250, update_chart)


def connect_menu_init():
    #########################################
    # Function to initialize the GUI
    #########################################
    global root, connect_btn, refresh_btn, graph, toggle_Pin_btn, get_ADC_btn, x, y, fig, line, chart, ax, xData, yData
    root = Tk()
    root.title("Serial communication")

    # the size as we have new Gui
    root.geometry("500x200")

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
    # btn to start / stop reading the ADC data
    get_ADC_btn = Button(root, text="Start ADC", height=2,
                         width=10, command=getADC)
    get_ADC_btn.grid(column=2, row=5)
    get_ADC_btn.grid_remove()

    # 2: Adding the graph widget to the Gui (Important to declare them as global)
    fig = plt.Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    chart = FigureCanvasTkAgg(fig, master=root)
    chart.get_tk_widget().grid(column=6, row=1, columnspan=6, rowspan=6)
    chart.get_tk_widget().grid_remove()

    # 3: Adding plotting variable (Important to declare them as global)
    xData = []
    yData = []
    x = []
    y = []


def connect_check(args):
    ################################################
    # Function to Enable disable the connect Btn
    ################################################
    if "-" in clicked_com.get() or "-" in clicked_bd.get():
        connect_btn["state"] = "disable"
    else:
        connect_btn["state"] = "active"


def baud_select():
    #############################################
    # Function to list the Baudes
    #############################################
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


def update_coms():
    ###########################################################
    # Function to Get the available COMs connected to the PC
    ###########################################################
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


def graph_control(graph):
    #################################################
    # Function (Thread 3) to Manage the GUI animation
    #################################################
    graph.canvas.itemconfig(
        graph.outer, exten=int(359*graph.sensor/1000))
    graph.canvas.itemconfig(
        graph.text, text=f"{int(3.3*graph.sensor)}")


def readSerial():
    ####################################################################
    # Function (Thread 2) to Manage Reading the UART data from MCU
    ####################################################################
    print("thread start")
    global serialData, graph, x, y, refTime
    average = 0
    sampling = 50
    sample = 0
    # 5 Adding 10 reads to clean the buffe
    for _ in range(10):
        try:
            data = ser.readline()
        except:
            pass

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
                    #############################################
                    # 8: Start recording the data into X and Y lists
                    yData.append((sensor*3.3)/1000)
                    if len(xData) == 0:
                        xData.append(0)
                    else:
                        xData.append(time.perf_counter()-refTime)
                    lenYdata = len(yData)
                    lenXdata = len(xData)
                    printRange = 0
                    TimeRange = 30  # The range in Sec I would like to see
                    for time_series in range(lenXdata-1, 0, -1):
                        printRange += 1
                        if xData[lenXdata-1] - xData[time_series - 1] > TimeRange:
                            break
                    if lenXdata == printRange:
                        y = [k for k in yData]
                        x = [k for k in xData]
                    else:
                        y = yData[lenYdata-printRange:lenYdata]
                        x = xData[lenYdata-printRange:lenYdata]
                    #############################################

                    graph.sensor = sensor
                    t2 = threading.Thread(target=graph_control, args=(graph,))
                    t2.deamon = True
                    t2.start()

            except:
                pass


def connexion():
    ###########################################################
    # Function to connect / Disconnect serial Com
    ###########################################################
    global ser, serialData, toggle_Pin_btn
    if connect_btn["text"] in "Disconnect":
        root.geometry("500x200")
        connect_btn["text"] = "Connect"
        refresh_btn["state"] = "active"
        drop_bd["state"] = "active"
        drop_COM["state"] = "active"
        toggle_Pin_btn.grid_remove()
        get_ADC_btn.grid_remove()

    else:
        root.geometry("500x300")
        connect_btn["text"] = "Disconnect"
        refresh_btn["state"] = "disable"
        drop_bd["state"] = "disable"
        drop_COM["state"] = "disable"
        port = clicked_com.get()
        baud = clicked_bd.get()
        try:
            ser = serial.Serial(port, baud, timeout=0)
        except:
            pass
        toggle_Pin_btn.grid()
        get_ADC_btn.grid()


def close_window():
    ######################################################
    # Dealing with interrupt issue at thread level
    #######################################################
    global root, serialData
    serialData = False
    time.sleep(0.5)
    root.destroy()


connect_menu_init()  # Start the GUI & Initialization
root.protocol("WM_DELETE_WINDOW", close_window)  # When Closing the Window
root.mainloop()  # Stating the main loop / Thread
