# Copyright 2021 <WeeW Stack >

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files(the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# For more content visit the WeeW Stack Channel on YouTube

from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import threading

# python -m pip install --upgrade matplotlib
import matplotlib.pyplot as plt  # pip install matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class RootGUI():
    def __init__(self, serial, data):
        '''Initializing the root GUI and other comps of the program'''
        self.root = Tk()
        self.root.title("Serial communication")
        self.root.geometry("360x120")
        self.root.config(bg="white")
        self.serial = serial
        self.data = data

        # Call function when the GUI is closed
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        '''Class to manage the ending of the gui, it is very import
        as it is managing the ending of threadings that were not stopped'''
        print("Closing the window and exit")
        self.root.destroy()
        self.serial.SerialClose(self)
        self.serial.threading = False


# Class to setup and create the communication manager with MCU
class ComGui():
    def __init__(self, root, serial, data):
        '''
        Initialize the connexion GUI and initialize the main widgets
        '''
        # Initializing the Widgets
        self.root = root
        self.serial = serial
        self.data = data
        self.frame = LabelFrame(root, text="Com Manager",
                                padx=5, pady=5, bg="white")
        self.label_com = Label(
            self.frame, text="Available Port(s): ", bg="white", width=15, anchor="w")
        self.label_bd = Label(
            self.frame, text="Baude Rate: ", bg="white", width=15, anchor="w")

        # Setup the Drop option menu
        self.baudOptionMenu()
        self.ComOptionMenu()

        # Add the control buttons for refreshing the COMs & Connect
        self.btn_refresh = Button(self.frame, text="Refresh",
                                  width=10,  command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect",
                                  width=10, state="disabled",  command=self.serial_connect)

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 5

        # Put on the grid all the elements
        self.publish()

    def publish(self):
        '''
         Method to display all the Widget of the main frame
        '''
        self.frame.grid(row=0, column=0, rowspan=3,
                        columnspan=3, padx=5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.label_bd.grid(column=1, row=3)

        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        self.btn_refresh.grid(column=3, row=2)
        self.btn_connect.grid(column=3, row=3)

    def ComOptionMenu(self):
        '''
         Method to Get the available COMs connected to the PC
         and list them into the drop menu
        '''
        # Generate the list of available coms

        self.serial.getCOMList()

        self.clicked_com = StringVar()
        self.clicked_com.set(self.serial.com_list[0])
        self.drop_com = OptionMenu(
            self.frame, self.clicked_com, *self.serial.com_list, command=self.connect_ctrl)

        self.drop_com.config(width=10)

    def baudOptionMenu(self):
        '''
         Method to list all the baud rates in a drop menu
        '''
        self.clicked_bd = StringVar()
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
        self.clicked_bd .set(bds[0])
        self.drop_baud = OptionMenu(
            self.frame, self.clicked_bd, *bds, command=self.connect_ctrl)
        self.drop_baud.config(width=10)

    def connect_ctrl(self, widget):
        '''
        Mehtod to keep the connect button disabled if all the
        conditions are not cleared
        '''
        print("Connect ctrl")
        # Checking the logic consistency to keep the connection btn
        if "-" in self.clicked_bd.get() or "-" in self.clicked_com.get():
            self.btn_connect["state"] = "disabled"
        else:
            self.btn_connect["state"] = "active"

    def com_refresh(self):
        print("Refresh")
        # Get the Widget destroyed
        self.drop_com.destroy()

        # Refresh the list of available Coms
        self.ComOptionMenu()

        # Publish the this new droplet
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        # Just in case to secure the connect logic
        logic = []
        self.connect_ctrl(logic)

    def serial_connect(self):
        '''
        Method that Updates the GUI during connect / disconnect status
        Manage serials and data flows during connect / disconnect status
        '''
        if self.btn_connect["text"] in "Connect":
            # Start the serial communication
            self.serial.SerialOpen(self)

            # If connection established move on
            if self.serial.ser.status:
                # Update the COM manager
                self.btn_connect["text"] = "Disconnect"
                self.btn_refresh["state"] = "disable"
                self.drop_baud["state"] = "disable"
                self.drop_com["state"] = "disable"
                InfoMsg = f"Successful UART connection using {self.clicked_com.get()}"
                messagebox.showinfo("showinfo", InfoMsg)

                # Display the channel manager
                self.conn = ConnGUI(self.root, self.serial, self.data)

                # Start Sync threading
                self.serial.t1 = threading.Thread(
                    target=self.serial.SerialSync, args=(self, ), daemon=True)
                self.serial.t1.start()

            else:
                ErrorMsg = f"Failure to estabish UART connection using {self.clicked_com.get()} "
                messagebox.showerror("showerror", ErrorMsg)
        else:

            # self.t1.terminate()
            self.serial.threading = False

            # Closing the Serial COM
            # Close the serial communication
            self.serial.SerialClose(self)

            # Closing the Conn Manager
            # Destroy the channel manager
            self.conn.ConnGUIClose()

            # Start Sync threading
            # Clear all the data from the Data manager
            self.data.ClearData()

            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed"
            messagebox.showwarning("showinfo", InfoMsg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"


class ConnGUI():
    def __init__(self, root, serial, data):
        '''
        Initialize main Widgets for communication GUI
        '''
        self.root = root
        self.serial = serial
        self.data = data

        # Build ConnGui Static Elements
        self.frame = LabelFrame(root, text="Connection Manager",
                                padx=5, pady=5, bg="white", width=60)
        self.sync_label = Label(
            self.frame, text="Sync Status: ", bg="white", width=15, anchor="w")
        self.sync_status = Label(
            self.frame, text="..Sync..", bg="white", fg="orange", width=5)

        self.ch_label = Label(
            self.frame, text="Active channels: ", bg="white", width=15, anchor="w")
        self.ch_status = Label(
            self.frame, text="...", bg="white", fg="orange", width=5)

        self.btn_start_stream = Button(self.frame, text="Start", state="disabled",
                                       width=5, command=self.start_stream)

        self.btn_stop_stream = Button(self.frame, text="Stop", state="disabled",
                                      width=5, command=self.stop_stream)

        self.btn_add_chart = Button(self.frame, text="+", state="disabled",
                                    width=5, bg="white", fg="#098577",
                                    command=self.new_chart)

        self.btn_kill_chart = Button(self.frame, text="-", state="disabled",
                                     width=5, bg="white", fg="#CC252C",
                                     command=self.kill_chart)
        self.save = False
        self.SaveVar = IntVar()
        self.save_check = Checkbutton(self.frame, text="Save data", variable=self.SaveVar,
                                      onvalue=1, offvalue=0, bg="white", state="disabled",
                                      command=self.save_data)

        self.separator = ttk.Separator(self.frame, orient='vertical')

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 15

        # Extending the GUI
        self.ConnGUIOpen()
        self.chartMaster = DisGUI(self.root, self.serial, self.data)

    def ConnGUIOpen(self):
        '''
        Method to display all the widgets
        '''
        self.root.geometry("800x120")
        self.frame.grid(row=0, column=4, rowspan=3,
                        columnspan=5, padx=5, pady=5)

        self.sync_label.grid(column=1, row=1)
        self.sync_status.grid(column=2, row=1)

        self.ch_label.grid(column=1, row=2)
        self.ch_status.grid(column=2, row=2, pady=self.pady)

        self.btn_start_stream.grid(column=3, row=1, padx=self.padx)
        self.btn_stop_stream.grid(column=3, row=2, padx=self.padx)

        self.btn_add_chart.grid(column=4, row=1, padx=self.padx)
        self.btn_kill_chart.grid(column=5, row=1, padx=self.padx)

        self.save_check.grid(column=4, row=2, columnspan=2)
        self.separator.place(relx=0.58, rely=0, relwidth=0.001, relheight=1)

    def ConnGUIClose(self):
        '''
        Method to close the connection GUI and destorys the widgets
        '''
        # Must destroy all the element so they are not kept in Memory
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("360x120")

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def new_chart(self):
        '''
        Method that will add a new char with all the options 
        '''
        try:
            self.chartMaster.AddChannelMaster()
        except:
            self.chartMaster = DisGUI(self.root, self.serial, self.data)

    def kill_chart(self):
        '''
        Method that will remove a chart and kill all the widgets inside it
        '''
        try:

            if len(self.chartMaster.frames) > 0:
                totalFrame = len(self.chartMaster.frames)-1
                self.chartMaster.frames[totalFrame].destroy()
                self.chartMaster.frames.pop()
                self.chartMaster.figs.pop()
                self.chartMaster.ControlFrames.pop()
                self.chartMaster.AdjustRootFrame()
        except:
            pass

    def save_data(self):
        pass


# Class to setup the data display GUI
class DisGUI():
    def __init__(self, root, serial, data):
        '''
        Method to initiate the objects that will be used to manage the GUI
        '''
        self.root = root
        self.serial = serial
        self.data = data
        # Master Frame controls
        self.frames = []
        self.framesCol = 0
        self.framesRow = 4
        self.totalframes = 0

        self.figs = []

        # The control Frame
        self.ControlFrames = []

    def AddChannelMaster(self):
        '''
        This method is a group of methods that will be used to generate a new frame
        that will include a chart and all the control Widgets
        '''
        self.AddMasterFrame()
        self.AdjustRootFrame()
        self.AddGraph()
        self.AddBtnFrame()

    def AddMasterFrame(self):
        '''
        This Method will add a new master frame wich will control all the element inside
        including the chart, the btns and the Drops
        '''
        self.frames.append(LabelFrame(self.root, text=f"Display Manager-{len(self.frames)+1}",
                                      pady=5, padx=5, bg="white"))
        self.totalframes = len(self.frames)-1
        # print(f'Total frames:{self.totalframes}')
        if self.totalframes % 2 == 0:
            self.framesCol = 0
        else:
            self.framesCol = 9
        # print(f'Col: {self.framesCol}')
        self.framesRow = 4 + 4 * int(self.totalframes / 2)
        # print(f'Row: {self.framesRow}')
        self.frames[self.totalframes].grid(padx=5,
                                           column=self.framesCol, row=self.framesRow, columnspan=8, sticky=NW)

    def AdjustRootFrame(self):
        '''
        This Method will generate the code related to adjusting
        the main root Gui based on the number of added GUI
        '''
        self.totalframes = len(self.frames)-1
        if self.totalframes > 0:
            RootW = 800*2

        else:
            RootW = 800

        if self.totalframes+1 == 0:
            RootH = 120
        else:
            RootH = 120 + 430 * (int(self.totalframes/2)+1)
        self.root.geometry(f"{RootW}x{RootH}")

    def AddGraph(self):
        '''
            This method will add setup the figure and the plot that will be used later on
            All the data will be inside the list to get an easier access later on
            '''
        # Setting up the plot for the each Frame
        self.figs.append([])
        # Initialize figures
        self.figs[self.totalframes].append(plt.Figure(figsize=(7, 5), dpi=80))
        # Initialize the plot
        self.figs[self.totalframes].append(
            self.figs[self.totalframes][0].add_subplot(111))
        # Initialize the chart
        self.figs[self.totalframes].append(FigureCanvasTkAgg(
            self.figs[self.totalframes][0], master=self.frames[self.totalframes]))

        self.figs[self.totalframes][2].get_tk_widget().grid(
            column=1, row=0, columnspan=4, rowspan=17,  sticky=N)

    def AddBtnFrame(self):
        '''
        Method to add the bottons to be used to add further channels 
        the button need to use a partial lib when calling the libary so it can keep the right 
        Widget target --> Further details in the YouTube WeeW-Stack
        '''
        btnH = 2
        btnW = 4
        self.ControlFrames.append([])
        self.ControlFrames[self.totalframes].append(LabelFrame(self.frames[self.totalframes],
                                                               pady=5, bg="white"))
        self.ControlFrames[self.totalframes][0].grid(
            column=0, row=0, padx=5, pady=5,  sticky=N)

        self.ControlFrames[self.totalframes].append(Button(self.ControlFrames[self.totalframes][0], text="+",
                                                           bg="white", width=btnW, height=btnH))
        self.ControlFrames[self.totalframes][1].grid(
            column=0, row=0, padx=5, pady=5)
        self.ControlFrames[self.totalframes].append(Button(self.ControlFrames[self.totalframes][0], text="-",
                                                           bg="white", width=btnW, height=btnH))
        self.ControlFrames[self.totalframes][2].grid(
            column=1, row=0, padx=5, pady=5)


if __name__ == "__main__":
    RootGUI()
    ComGui()
    ConnGUI()
