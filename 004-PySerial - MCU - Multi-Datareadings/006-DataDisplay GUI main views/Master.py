from GUI_Master import RootGUI, ComGui
from Serial_Com_ctrl import SerialCtrl
from Data_Com_ctrl import DataMaster

MySerial = SerialCtrl()
MyData = DataMaster()
RootMaster = RootGUI(MySerial, MyData)

ComMaster = ComGui(RootMaster.root, MySerial, MyData)

RootMaster.root.mainloop()
