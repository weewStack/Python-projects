import time
import numpy as np

from scipy.signal import savgol_filter
from scipy import signal

from datetime import datetime
import csv


class DataMaster():

    def __init__(self):
        self.sync = "#?#\n"
        self.sync_ok = "!"
        self.StartStream = "#A#\n"
        self.StopStream = "#S#\n"
        self.SynchChannel = 0

        self.msg = []

        self.XData = []
        self.YData = []

        self.FunctionMaster = {
            "RowData": self.RowData,
            "VoltageDisplay": self.VoltData,
            "ColorFilter": self.ColorFilter,
            "SavgolFilter": self.SavgolFilter,
            "DigitalFilter": self.DigitalFilter
        }

        self.DisplayTimeRange = 5

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

    def FileNameFunc(self):
        now = datetime.now()
        self.filename = now.strftime("%Y%m%d%H%M%S")+".csv"

    def SaveData(self, gui):
        data = [elt for elt in self.IntMsg]
        data.insert(0, self.XData[len(self.XData)-1])
        if gui.save:
            with open(self.filename, 'a', newline='') as f:
                data_writer = csv.writer(f)
                data_writer.writerow(data)

    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf8')
        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                del self.msg[0]
                if self.msg[0] in "D":
                    self.messageLen = 0
                    self.messageLenCheck = 0
                    del self.msg[0]
                    del self.msg[len(self.msg)-1]
                    self.messageLen = int(self.msg[len(self.msg)-1])
                    del self.msg[len(self.msg)-1]
                    for item in self.msg:
                        self.messageLenCheck += len(item)

    def GenChannels(self):
        self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]

    def buildYdata(self):
        self.YData = []
        for _ in range(self.SynchChannel):
            self.YData.append([])

    def ClearData(self):
        self.RowMsg = ""
        self.msg = []
        self.YData = []
        self.XData = []

    def IntMsgFunc(self):
        self.IntMsg = [int(msg) for msg in self.msg]

    def StreamDataCheck(self):
        self.StreamData = False
        if self.SynchChannel == len(self.msg):
            if self.messageLen == self.messageLenCheck:
                self.StreamData = True
                self.IntMsgFunc()

    def SetRefTime(self):
        if len(self.XData) == 0:
            self.RefTime = time.perf_counter()
        else:
            self.RefTime = time.perf_counter() - self.XData[len(self.XData)-1]

    def UpdataXdata(self):
        if len(self.XData) == 0:
            self.XData.append(0)
        else:
            self.XData.append(time.perf_counter()-self.RefTime)

    def UpdataYdata(self):
        for ChNumber in range(self.SynchChannel):
            self.YData[ChNumber].append(self.IntMsg[ChNumber])

    def AdjustData(self):
        lenXdata = len(self.XData)
        if (self.XData[lenXdata-1] - self.XData[0]) > self.DisplayTimeRange:
            del self.XData[0]
            for ydata in self.YData:
                del ydata[0]

        x = np.array(self.XData)
        self.XDisplay = np.linspace(x.min(), x.max(), len(x), endpoint=0)
        self.YDisplay = np.array(self.YData)

    def RowData(self, gui):
        gui.chart.plot(gui.x, gui.y, color=gui.color,
                       dash_capstyle='projecting', linewidth=1)

    def VoltData(self, gui):
        gui.chart.plot(gui.x, (gui.y/4096)*3.3, color=gui.color,
                       dash_capstyle='projecting', linewidth=1)

    def SavgolFilter(self, gui):
        x = gui.x
        y = gui.y
        w = savgol_filter(y, 1001, 2)
        gui.chart.plot(x, w, color="#db2775",
                       dash_capstyle='projecting', linewidth=2)

    def DigitalFilter(self, gui):
        x = gui.x
        y = gui.y
        b, a = signal.ellip(4, 0.01, 120, 0.125)
        fgust = signal.filtfilt(b, a, y, method="gust")
        gui.chart.plot(x, fgust, color="#1cbda5",
                       dash_capstyle='projecting', linewidth=2)

    def ColorFilter(self, gui):
        '''
        Mehtod that will display a different color based on the value
        '''
        limit = 2000
        y = gui.y
        x = gui.data.XDisplay
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
