import tkinter as tk

class ConnectionDialog():
    def show(this):
        window = tk.Tk()
        window.title("PiRover Client App")

        tk.Label(master=window, text="Enter details to connect to the PiRover").grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(master=window, text="Host name or ip address:").grid(row=1, column=0, sticky="w")
        ent_server_address = tk.Entry(master=window)
        ent_server_address.grid(row=1, column=1, sticky="w")

        tk.Label(master=window, text="Port:").grid(row=2, column=0, sticky="w")
        ent_server_port = tk.Entry(master=window)
        ent_server_port.insert(0, "1987")
        ent_server_port.grid(row=2, column=1, sticky="w")

        tk.Label(master=window, text="Password:").grid(row=3, column=0, sticky="w")
        ent_password = tk.Entry(master=window, show="*")
        ent_password.insert(0, "uMieY6ophu[a")
        ent_password.grid(row=3, column=1, sticky="w")

        tk.Label(master=window, text="Options:").grid(row=4, column=0, sticky="w")
        cbx_record_video = tk.Checkbutton(master=window, text="Record video")
        cbx_record_video.grid(row=4, column=1, sticky="w")

        btn_cancel = tk.Button(master=window, text="Cancel", width=17)
        btn_cancel.grid(row=5, column=0)
        btn_connect = tk.Button(master=window, text="Okay", width=17)
        btn_connect.grid(row=5, column=1)

        window.mainloop()