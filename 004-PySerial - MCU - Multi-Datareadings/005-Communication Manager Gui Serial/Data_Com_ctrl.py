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
        self.msg = []
        # Build the Ydata
        self.YData = []
        self.XData = []

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

    def GenChannels(self):
        '''
        Mehtod to Generate the list of Channels to be used for the selection
        '''
        self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]

    def buildYdata(self):
        '''
            Message to get the right size of the data to be inputted into the Y data
            '''
        for _ in range(self.SynchChannel):
            self.YData.append([])

    def ClearData(self):
        '''
        Mehtod used to clear the data after each new serial updload
        '''
        self.RowMsg = ""
        self.msg = []
        self.YData = []


if __name__ == "__main__":
    DataMaster()
