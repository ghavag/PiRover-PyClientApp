from . import connectiondialog

print("PiRover client app started!")
cd = connectiondialog.ConnectionDialog()
if cd.show():
    input("Press the Enter key to close connection.") 
