from GUI_Master import RootGUI, ComGui


RootMaster = RootGUI()

ComMaster = ComGui(RootMaster.root)

RootMaster.root.mainloop()
