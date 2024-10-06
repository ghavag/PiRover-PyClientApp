from . import connectiondialog

print("Hello World!")
cd = connectiondialog.ConnectionDialog()
cd.show()
print(cd.connection_params)