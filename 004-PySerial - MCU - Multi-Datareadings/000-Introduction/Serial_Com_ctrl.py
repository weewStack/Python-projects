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

import serial.tools.list_ports  # pip install pyserial
import time
import threading


# Secure the UART serial communication with MCU
class SerialCtrl():
    def __init__(self):
        '''
        Initializing the main varialbles for the serial data
        '''
        self.threading = False

        self.sync_time = 0.01
        self.sync_cnt = 200

        self.StreamRecall = 2000
        self.StreamCnt = 0

    def getCOMList(self):
        '''
        Method that get the lost of available coms in the system
        '''
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0, "-")

    def SerialOpen(self, ComGUI):
        '''
        Method to setup the serial connection and make sure to go for the next only 
        if the connection is done properly
        '''

        try:
            self.ser.is_open
        except:
            PORT = ComGUI.clicked_com.get()
            BAUD = ComGUI.clicked_bd.get()
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = 0.1

        try:
            if self.ser.is_open:
                print("Already Open")
                self.ser.status = True
            else:
                PORT = ComGUI.clicked_com.get()
                BAUD = ComGUI.clicked_bd.get()
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = 0.01
                self.ser.open()
                self.ser.status = True
        except:
            self.ser.status = False

    def SerialClose(self, ComGUI):
        '''
        Method used to close the UART communication
        '''
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
        except:
            self.ser.status = False

    def SerialSync(self, gui):
        '''
        Method to make sure that the MCU is using the same synchronizing protocol
        then establish the communication
        This method will show if the Sync is ok or failed + shows the number of available channels
        '''
        self.threading = True

        time.sleep(0.2)
        cnt = 0
        while self.threading:
            try:
                self.ser.write(gui.data.sync.encode())
                gui.conn.sync_status["text"] = "..Sync.."
                gui.conn.sync_status["fg"] = "orange"
                gui.data.RowMsg = self.ser.readline()
                gui.data.DecodeMsg()
                if gui.data.sync_ok in gui.data.msg[0]:
                    if int(gui.data.msg[1]) > 0:
                        gui.conn.btn_start_stream["state"] = "active"
                        gui.conn.btn_add_chart["state"] = "active"
                        gui.conn.btn_kill_chart["state"] = "active"
                        gui.conn.save_check["state"] = "active"
                        gui.conn.sync_status["text"] = "OK"
                        gui.conn.sync_status["fg"] = "green"
                        gui.conn.ch_status["fg"] = "green"
                        gui.conn.ch_status["text"] = gui.data.msg[1]
                        gui.data.SynchChannel = int(gui.data.msg[1])
                        gui.data.GenChannels()
                        gui.data.buildYdata()
                        gui.data.FileNameFunc()
                        self.threading = False
                        break
            except Exception as e:
                print(e)
            cnt += 1

            if self.threading == False:
                break
            if cnt > self.sync_cnt:
                gui.conn.sync_status["text"] = "failed"
                gui.conn.sync_status["fg"] = "red"
                time.sleep(0.5)
                cnt = 0
                if self.threading == False:
                    break

    def SerialDataStream(self, gui):
        self.threading = True
        while self.threading:
            try:
                self.ser.write(gui.data.StartStream.encode())
                gui.data.RowMsg = self.ser.readline()
                gui.data.DecodeMsg()
                gui.data.StreamDataCheck()
                if gui.data.StreamData:
                    gui.data.SetReftime()
                    break
            except:
                pass
        gui.UpdateChart()
        while self.threading:
            try:
                gui.data.RowMsg = self.ser.readline()

                gui.data.DecodeMsg()
                gui.data.StreamDataCheck()
                if gui.data.StreamData:
                    gui.data.UpdateYdata()
                    gui.data.UpdateXdata()
                    t1 = threading.Thread(
                        target=gui.data.AdjustData, daemon=True)
                    t1.start()
                    if gui.save:
                        t2 = threading.Thread(
                            target=gui.data.SaveData, args=(gui,), daemon=True)
                        t2.start()

            except:
                pass
