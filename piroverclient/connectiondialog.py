from tkinter import *
from tkinter import ttk, messagebox

class ConnectionDialog():
    def __init__(self):
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

    def show(self):
        self.connection_params = None
        self.window.mainloop()

    def _on_connect(self):
        print("On connect")
        self.ent_server_address["style"] = ""
        self.ent_server_port["style"] = ""

        if (res := self._validate()):
            self.connection_params = {'password': self.ent_password.get(), 'record_video': self.record_video.get()}
            self.connection_params.update(res)
            self.window.destroy()

    def _validate(self):
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

        return {'address': hostname, 'port': port}

    # https://stackoverflow.com/questions/2532053/validate-a-hostname-string
    def _is_valid_hostname(self, hostname):
        if len(hostname) < 1 or len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present

        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))
