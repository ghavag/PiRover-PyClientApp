# Copyright (c) 2024 Alexander Graeb
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# (see LICENSE_LGPLv3) along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

import socket
import re
import hashlib
from tkinter import *
from tkinter import ttk, messagebox

class ConnectionDialog():
"""
Class responsible for showing a dialog that asks for all parameters
required to connect to the PiRover server, like hostname and port.
"""
    def __init__(self):
        """
        Class constructor. Setups the GUI elements.
        """
        self.sock = None

        self.window = Tk()
        self.window.title("PiRover Client App")

        style = ttk.Style()
        style.configure("BW.TLabel", background="#ff8888")

        self.frm = ttk.Frame(self.window, padding=10)
        self.frm.grid()

        ttk.Label(master=self.frm, text="Enter details to connect to the PiRover").grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(master=self.frm, text="Host name or ip address:").grid(row=1, column=0, sticky="w")
        self.ent_server_address = ttk.Entry(master=self.frm)
        self.ent_server_address.grid(row=1, column=1, sticky="w")

        ttk.Label(master=self.frm, text="Port:").grid(row=2, column=0, sticky="w")
        self.ent_server_port = ttk.Entry(master=self.frm)
        self.ent_server_port.insert(0, "1987")
        self.ent_server_port.grid(row=2, column=1, sticky="w")

        ttk.Label(master=self.frm, text="Password:").grid(row=3, column=0, sticky="w")
        self.ent_password = ttk.Entry(master=self.frm, show="*")
        self.ent_password.insert(0, "uMieY6ophu[a")
        self.ent_password.grid(row=3, column=1, sticky="w")

        ttk.Label(master=self.frm, text="Options:").grid(row=4, column=0, sticky="w")
        self.record_video = IntVar()
        self.cbx_record_video = ttk.Checkbutton(master=self.frm, text="Record video", variable=self.record_video)
        self.cbx_record_video.grid(row=4, column=1, sticky="w")

        self.btn_cancel = ttk.Button(master=self.frm, text="Cancel", command=self.window.destroy, width=17)
        self.btn_cancel.grid(row=5, column=0)
        self.btn_connect = ttk.Button(master=self.frm, text="Okay", command=self._on_connect, width=17)
        self.btn_connect.grid(row=5, column=1)

    def __del__(self):
        """
        Class destructor. Closes the socket if it existed then the class
        is destroyed. The class must live during the lifetime of the whole
        client app.
        """
        if self.sock:
            self.sock.close()
    
    def show(self):
        """
        Shows the dialog. Blocks until the dialog has been closed.
        Returns true, if the user initiated the connection to the
        PiRover server and the validation has been passed and false
        otherwise.
        """
        self.window.mainloop()
        return self.sock != None

    def _on_connect(self):
        """
        Called by the GUI if the user clicked the button to connect.
        Does validation of the input data and connects to the PiRover
        server. Closes the dialog if the connection has been successfully
        established.
        """
        self.ent_server_address["style"] = ""
        self.ent_server_port["style"] = ""

        if (self._validate()):
            try:
                self._connect_to_pirover()
            except Exception as e:
                messagebox.showerror("Unable to connect", e)
            else:
                self.window.destroy()

    def _validate(self):
        """
        Does very basic validation on entered hostname and port. Returns
        true on success and false otherwise.
        """
        hostname = self.ent_server_address.get()
        
        if not self._is_valid_hostname(hostname):
            self.ent_server_address["style"] = "BW.TLabel"
            messagebox.showerror("Invalid hostname", "Please enter a valid hostname or IP address")
            return False

        port = False

        try:
            port = int(self.ent_server_port.get())
        except ValueError:
            pass
        else:
            if port < 1 or port > 65535:
                port = False
        
        if not port:
            self.ent_server_port["style"] = "BW.TLabel"
            messagebox.showerror("Invalid port", "Please enter a valid port number.")
            return False

        self.hostname = hostname
        self.port = port

        return True

    def _is_valid_hostname(self, hostname):
        """
        Validates a hostname and return true if the hostname is valid and
        false otherwise. Got inspired from:
        https://stackoverflow.com/questions/2532053/validate-a-hostname-string
        """
        if len(hostname) < 1 or len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present

        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def _connect_to_pirover(self):
        """
        Establishes a connection to a PiRover server and performs the
        authentication.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
    
        try:
            self.sock.connect((self.hostname, self.port))
        except OSError as e:
            self.sock.close()
            raise e
        
        msg = "Hello PiRover!"
        # TODO: Append flags to message
        print("We:", msg)
        self.sock.send(msg.encode())

        answer = self.sock.recv(256)
        print("PiRover:", answer.decode())
        m = re.match(r'PiRover \d+\.\d+ here! (\d+\.?\d+)', answer.decode())
        
        if not m:
            print("Invalid respond from PiRover!")
            raise Exception("Something responded, but it doesn't seem to be a PiRover server.")
        
        print("Salt is:", m.group(1))

        pw = self.ent_password.get()
        msg = hashlib.md5((pw + m.group(1)).encode()).hexdigest() + "\n"
        print("We:", msg)
        self.sock.send(msg.encode())

        answer = self.sock.recv(256).decode()
        print("PiRover:", answer)

        if answer != "OK\n":
            raise Exception("Authentication with PiRover failed. Invalid password?")

        print("Connection successfully established!")
        