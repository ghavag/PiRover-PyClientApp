from tkinter import *
from tkinter import ttk, messagebox
import threading
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, GLib, GstVideo

# How long a single key press lasts (as opposed to a press-and-hold).
SINGLE_PRESS_MAX_SECONDS = 0.05

class Debouncer(object):
"""
Debounces key events for Tkinter apps, so that press-and-hold works.
Code for class borrowed from https://github.com/adamheins/tk-debouncer
"""
    def __init__(self, pressed_cb, released_cb):
        self.key_pressed = False
        self.key_released_timer = None

        self.pressed_cb = pressed_cb
        self.released_cb = released_cb


    def _key_released_timer_cb(self, event):
        ''' Called when the timer expires for a key up event, signifying that a
            key press has actually ended. '''
        self.key_pressed = False
        self.released_cb(event)


    def pressed(self, event):
        ''' Callback for a key being pressed. '''
        # If timer set by up is active, cancel it, because the press is still
        # active.
        if self.key_released_timer:
            self.key_released_timer.cancel()
            self.key_released_timer = None

        # If the key is not currently pressed, mark it so and call the callback.
        if not self.key_pressed:
            self.key_pressed = True
            self.pressed_cb(event)


    def released(self, event):
        ''' Callback for a key being released. '''
        # Set a timer. If it is allowed to expire (not reset by another down
        # event), then we know the key has been released for good.
        self.key_released_timer = threading.Timer(SINGLE_PRESS_MAX_SECONDS,
                                        self._key_released_timer_cb, [event])
        self.key_released_timer.start()

class ControlWindow():
"""
Class wrapping the code for the control windows.
"""
    def __init__(self, socket):
        """
        Class constructor. Setups the GUI elements and sets up the
        GStreamer pipelines for receiving video and audio.
        """
        self.sock = socket

        self.window = Tk()
        self.window.resizable(height=False, width=False)
        self.window.title("PiRover Client App")
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.canvas = Canvas(self.window, width=800, height=600, bg="black")
        self.canvas.pack()
        self.canvas.create_text(400, 300, text="Waiting for video stream...", fill="red")

        self.debouncer_right = Debouncer(self._key_pressed, self._key_released)
        self.window.bind('<KeyPress-Right>', self.debouncer_right.pressed)
        self.window.bind('<KeyRelease-Right>', self.debouncer_right.released)

        self.debouncer_left = Debouncer(self._key_pressed, self._key_released)
        self.window.bind('<KeyPress-Left>', self.debouncer_left.pressed)
        self.window.bind('<KeyRelease-Left>', self.debouncer_left.released)

        self.debouncer_up = Debouncer(self._key_pressed, self._key_released)
        self.window.bind('<KeyPress-Up>', self.debouncer_up.pressed)
        self.window.bind('<KeyRelease-Up>', self.debouncer_up.released)

        self.debouncer_down = Debouncer(self._key_pressed, self._key_released)
        self.window.bind('<KeyPress-Down>', self.debouncer_down.pressed)
        self.window.bind('<KeyRelease-Down>', self.debouncer_down.released)

        self.keep_alive_thread = threading.Thread(target=self._keep_alive_thread)
        self.keep_alive_thread.start()

        # Set up the gstreamer pipeline
        Gst.init(None)
        self.vid_player = Gst.parse_launch("udpsrc uri=udp://0.0.0.0:5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! xvimagesink")
        bus = self.vid_player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self._on_message)
        bus.connect("sync-message::element", self._on_sync_message)
        self.vid_player.set_state(Gst.State.PLAYING)

        self.aud_player = Gst.parse_launch("udpsrc address=0.0.0.0 port=5001 ! mpegaudioparse ! mpg123audiodec ! audioconvert ! autoaudiosink")
        self.aud_player.set_state(Gst.State.PLAYING)

    def show(self):
        """
        Shows the control window and blocks until the user closes it.
        """
        self.window.mainloop()
        self.keep_alive_thread = None
    
    def _key_pressed(self, event):
        """
        Called by the GUI on key pressed events for an arrow key.
        """
        msg = None

        if event.keysym == "Up":
            msg = "UP pressed\n"
        elif event.keysym == "Down":
            msg = "DOWN pressed\n"
        elif event.keysym == "Left":
            msg = "LEFT pressed\n"
        elif event.keysym == "Right":
            msg = "RIGHT pressed\n"

        if msg:
            print(msg)
            self.sock.send(msg.encode())
    
    def _key_released(self, event):
        """
        Called by the GUI on key release events for an arrow key.
        """
        msg = None

        if event.keysym == "Up":
            msg = "UP released\n"
        elif event.keysym == "Down":
            msg = "DOWN released\n"
        elif event.keysym == "Left":
            msg = "LEFT released\n"
        elif event.keysym == "Right":
            msg = "RIGHT released\n"

        if msg:
            print(msg)
            self.sock.send(msg.encode())

    def _keep_alive_thread(self):
        """
        That function sends regular keep alive messages to the PiRover
        server.
        """
        msg = "Keep alive\n"
        while self.keep_alive_thread:
            print(msg)
            self.sock.send(msg.encode())
            time.sleep(1)

    def _on_message(self, bus, message):
        """
        Handles messages from GStreamer bus.
        """
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.vid_player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.vid_player.set_state(gst.STATE_NULL)

    def _on_sync_message(self, bus, message):
        """
        Handles sync-message from GStreamer bus.
        """
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.canvas.winfo_id())

    def _on_closing(self):
        """
        Handles teardown of GStreamer pipelines etc. if the user closes
        the control windows and thus the whole client app.
        """
        self.vid_player.set_state(Gst.State.NULL)
        self.aud_player.set_state(Gst.State.NULL)
        self.window.destroy()
