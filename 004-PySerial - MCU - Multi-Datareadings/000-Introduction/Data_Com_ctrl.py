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

import time
from datetime import datetime
import csv

import numpy as np
import scipy.interpolate as si
from scipy.interpolate import interp1d
from scipy.signal import lfilter, savgol_filter
from scipy import signal


class DataMaster():
    def __init__(self):
        '''
        Method to initialize the Data class
        This classes will manage data transformation within the whole program 
        '''
        # Program Logic to interface with MCU
        self.sync = "#?#\n"
        self.sync_ok = "!"
        self.StartStream = "#A#\n"
        self.StopStream = "#S#\n"
        self.SynchChannel = 0

        # Dico to be used for building the list in dropup Widget
        # and all call the functions related to data transform

        self.FunctionMaster = {
            "RowData": self.RowData,
            "VolageDisplay": self.VoltData,
            "ColorFilter": self.ColorFilter,
            "ExpoSmooth": self.ExpoSmooth,
            "CubicInter": self.CubicInter,
            "BasicFilter": self.BasicFilter,
            "SavgolFilter": self.SavgolFilter,
            "PolyFilter": self.PolyFilter,
            "MedFilter": self.MedFilter,
            "filtfiltGaus": self.filtfiltGaus,
            "filtfiltPad": self.filtfiltPad
        }

        # Build the Ydata
        self.YData = []
        self.YDisplayData = []

        self.XData = []
        self.XDisplayData = []

        self.DisplayTimeRange = 5
        self.PrintRange = 0

        self.RefTime = 0

        self.ChannelColor = {
            'Ch0': 'blue',
            'Ch1': 'green',
            'Ch2': 'red',
            'Ch3': 'cyan',
            'Ch4': 'magenta',
            'Ch5': 'yellow',
            'Ch6': 'black',
            'Ch7': 'white'
        }
        self.ChannelNum = {
            'Ch0': 0,
            'Ch1': 1,
            'Ch2': 2,
            'Ch3': 3,
            'Ch4': 4,
            'Ch5': 5,
            'Ch6': 6,
            'Ch7': 7
        }

    def DataCleaning(self):
        '''Method to be discretly used When the connection is closed'''
        self.SynchChannel = 0
        self.YData = []
        self.YDisplayData = []
        self.XData = []
        self.XDisplayData = []
        self.RefTime = 0

    def FileNameFunc(self):
        '''
        A discrete method that will generate the file name when the connection is established
        '''
        now = datetime.now()
        self.filename = now.strftime("%Y%m%d%H%M%S")+".csv"

    def DecodeMsg(self):
        '''
        Method used to get the message coming from UART and converted to a python string
        it is also used to get defferent type of messages based on the Message protocol
        '''
        temp = self.RowMsg.decode('utf8')
        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                # print(self.msg)
                del self.msg[0]
                if self.msg[0] in "D":
                    self.messageLen = 0
                    self.messageLenCheck = 0
                    del self.msg[0]  # Removing the Signal at the beginning
                    del self.msg[len(self.msg)-1]  # removing the /n at the end
                    self.messageLen = int(self.msg[len(self.msg)-1])
                    # removing the check number at the end
                    del self.msg[len(self.msg)-1]
                    for item in self.msg:
                        self.messageLenCheck += len(item)

    def StreamDataCheck(self):
        '''
        Method to check if the message is 100 percent correct and can be
        used as correct data 
        '''
        self.StreamData = False
        if self.SynchChannel == len(self.msg):
            if self.messageLen == self.messageLenCheck:
                self.StreamData = True
                self.IntMsgFunc()

    def IntMsgFunc(self):
        '''
        Method that transform the string recieved message to an Int
        '''
        # print(self.msg)
        self.IntMsg = [int(msg) for msg in self.msg]

    def buildYdata(self):
        '''
        Message to get the right size of the data to be inputted into the Y data
        '''
        for _ in range(self.SynchChannel):
            self.YData.append([])

    def SetReftime(self):
        if len(self.XData) == 0:
            self.RefTime = time.perf_counter()
        else:
            self.RefTime = time.perf_counter()-self.XData[len(self.XData)-1]

    def UpdateYdata(self):
        '''
        Add the new serial data to the main list that will be used for the display
        '''
        for ChNumber in range(self.SynchChannel):
            self.YData[ChNumber].append(self.IntMsg[ChNumber])

    def UpdateXdata(self):
        '''
        add the new X value (Which time in this example)
        '''
        if len(self.XData) == 0:
            self.XData.append(0)
        else:
            self.XData.append(time.perf_counter()-self.RefTime)

    def SaveData(self, gui):
        '''
        Method used to save the data into a csv file
        '''
        data = [elt for elt in self.IntMsg]
        data.insert(0, self.XData[len(self.XData)-1])
        if gui.save:
            with open(self.filename, 'a', newline='') as f:
                data_writer = csv.writer(f)
                data_writer.writerow(data)

    def AdjustData(self):
        '''
        Method to adjust the display data at the required interval
        '''
        lenXdata = len(self.XData)
        if self.XData[lenXdata-1] - self.XData[0] > self.DisplayTimeRange:
            del self.XData[0]
            for ydata in self.YData:
                del ydata[0]
        x = np.array(self.XData)
        self.XDisplay = np.linspace(
            x.min(), x.max(), len(x), endpoint=False)
        self.YDisplay = np.array(self.YData)

    def ClearData(self):
        '''
        Mehtod used to clear the data after each new serial updload
        '''
        self.RowMsg = ""
        self.msg = []
        self.YData = []

    def GenChannels(self):
        '''
        Mehtod to Generate the list of Channels to be used for the selection
        '''
        self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]

    def RowData(self, gui):
        '''
        Method to display the raw recieved data
        '''
        gui.chart.plot(
            gui.data.XDisplay, gui.y, "-", dash_capstyle='projecting',  color=gui.color, linewidth=1)

    def VoltData(self, gui):
        '''
        Method to display the raw recieved data
        '''
        gui.chart.plot(
            gui.data.XDisplay, 3.3*(gui.y/4096), "-", dash_capstyle='projecting',  color=gui.color, linewidth=1)

    def ColorFilter(self, gui):
        '''
        Mehtod that will display a different color based on the value
        '''
        limit = 2000
        y = gui.y
        x = gui.data.XDisplay
        print(limit)
        chart = gui.chart
        color_master = np.array(
            ['r' if k > limit else 'g' for k in y])
        limit_array = np.array(
            [limit for k in range(len(x))])
        chart.plot(x, limit_array, c='blue')
        color_0 = color_master[0]
        start_seg = 0
        for cnt in range(len(color_master)):
            if color_0 == color_master[cnt+1]:
                color_0 = color_master[cnt+1]
            else:
                chart.plot(x[start_seg:cnt+1], y[start_seg:cnt+1], c=color_0)
                start_seg = cnt
                color_0 = color_master[cnt+1]
            if (cnt + 2) == len(color_master):
                chart.plot(x[start_seg:cnt+1], y[start_seg:cnt+1], c=color_0)
                break
        chart.set_ylim([0, 4096])

    def ExpoSmooth(self, DisplayGui):

        self.MyDisplayGui = DisplayGui
        x = self.XDisplay
        y = DisplayGui.y
        a_BSpline = si.make_interp_spline(self.XData, y)
        y_BSpline = a_BSpline(x)
        DisplayGui.chart.plot(
            x, y_BSpline, "-", dash_capstyle='projecting',  color=DisplayGui.color)

    def CubicInter(self, DisplayGui):
        x = self.XDisplay
        y = DisplayGui.y
        cubic_interploation_model = interp1d(
            self.XData, y, kind="cubic")
        Y_ = cubic_interploation_model(x)
        DisplayGui.chart.plot(
            x, Y_, "-", dash_capstyle='projecting', label='MyChannel',  color=DisplayGui.color)

    def BasicFilter(self, DisplayGui):
        '''
        Mehtod to apply a basic filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        n = 15  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        yy = lfilter(b, a, y)
        DisplayGui.chart.plot(
            x[50:len(x)-1], yy[50:len(x)-1], "-", dash_capstyle='projecting', color="#4abd1c", linewidth=2)

    def SavgolFilter(self, DisplayGui):
        '''
        Mehtod to apply a SavgolFilter filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        w = savgol_filter(y, 1001, 2)
        DisplayGui.chart.plot(
            x, w, "-", dash_capstyle='projecting',  color="#db2775", linewidth=4)

    def PolyFilter(self, DisplayGui):
        '''
        Mehtod to apply a PolyFilter filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        new_x = np.linspace(
            x.min(), x.max(), len(x)*20, endpoint=False)
        f_poly = signal.resample_poly(y, len(x)*20, len(x))
        DisplayGui.chart.plot(
            new_x[200:len(x)*20-200], f_poly[200:len(x)*20-200],  "-", dash_capstyle='projecting', label='MyChannel',  color=DisplayGui.color)

    def MedFilter(self, DisplayGui):
        '''
        Mehtod to apply a MedFilter filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        new_y = signal.medfilt(y, 1001)
        DisplayGui.chart.plot(
            x[20:len(x)-20], new_y[20:len(x)-20], "-", dash_capstyle='projecting', label='MyChannel',  color="#db9c27", linewidth=4)

    def filtfiltGaus(self, DisplayGui):
        '''
        Mehtod to apply a filtfiltGaus filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        b, a = signal.ellip(4, 0.01, 120, 0.125)
        fgust = signal.filtfilt(
            b, a, y, method="gust")
        DisplayGui.chart.plot(
            x, fgust, "-", dash_capstyle='projecting', label='MyChannel',  color="#1cbda5", linewidth=1)

    def filtfiltPad(self, DisplayGui):
        '''
        Mehtod to apply a filtfiltPad filter on the data to clean the noise
        '''
        x = self.XDisplay
        y = DisplayGui.y
        b, a = signal.ellip(4, 0.01, 120, 0.125)
        yhat = signal.filtfilt(
            b, a, y, padlen=3)
        DisplayGui.chart.plot(
            x, yhat, "-", dash_capstyle='projecting', label='MyChannel',  color="#b21cbd", linewidth=1)


if __name__ == "__main__":
    DataMaster()
