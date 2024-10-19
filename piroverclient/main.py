import sys
from . import connectiondialog, controlwindow

print("PiRover client app started!")
cd = connectiondialog.ConnectionDialog()

if not cd.show():
    sys.exit(0)

cw = controlwindow.ControlWindow()
cw.show()
