"""Desktop launcher for the one-board navigator; also the PyInstaller entry point."""

import contextlib
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from main import NavigatorSession
from serial_manager import SerialManager


class QueueWriter:
    def __init__(self, events):
        self.events = events

    def write(self, text):
        if text:
            self.events.put(("log", text))
        return len(text)

    def flush(self):
        pass


def run_backend(port, stop, events, manager_factory=SerialManager):
    """Keep serial I/O off the GUI thread and always release the port on stop."""
    manager = manager_factory(port)
    stream = QueueWriter(events)
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        try:
            manager.connect()
            if stop.is_set():
                return
            events.put(("status", "Connected — choose your route on the joystick"))
            session = NavigatorSession(manager)
            print("Choose START and DESTINATION on the device.")
            while not stop.is_set():
                message = manager.read_control()
                if message is None:
                    stop.wait(0.01)
                else:
                    session.handle(message)
        except Exception as error:
            events.put(("error", str(error)))
        finally:
            try:
                manager.close()
            except Exception as error:
                events.put(("log", f"Error closing serial port: {error}\n"))
            events.put(("stopped", None))


class NavigatorApp:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.worker = None
        self.closing = False
        self.ports = {}
        root.title("SFU Navigator")
        root.geometry("780x550")
        root.minsize(640, 450)
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        outer = ttk.Frame(root, padding=20)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="SFU Navigator", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(outer, text="One Arduino · Joystick controls · Campus landmark guidance").pack(anchor="w", pady=(2, 16))

        controls = ttk.Frame(outer)
        controls.pack(fill="x")
        ttk.Label(controls, text="Arduino port").pack(side="left", padx=(0, 10))
        self.port = ttk.Combobox(controls, state="readonly", width=40)
        self.port.pack(side="left", fill="x", expand=True)
        self.refresh_button = ttk.Button(controls, text="Refresh", command=self.refresh_ports)
        self.refresh_button.pack(side="left", padx=(8, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=12)
        self.start_button = ttk.Button(actions, text="Start navigator", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(actions, text="Stop", command=self.disconnect, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        self.status = tk.StringVar(value="Connect your Arduino, then select its port")
        ttk.Label(outer, textvariable=self.status, wraplength=720).pack(anchor="w", pady=(0, 8))

        tips = (
            "1. Upload the included joystick sketch once.  2. Close Arduino Serial Monitor.\n"
            "3. Start here, then choose START and DESTINATION on the device.\n"
            "Joystick left/right: previous/next · Click and release: select · Hold 1.2 s: reset"
        )
        ttk.Label(outer, text=tips, wraplength=720, justify="left").pack(anchor="w", pady=(0, 12))
        self.log = ScrolledText(outer, height=12, font=("Consolas", 10), wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)
        ttk.Label(outer, text="Prototype routes and distances need verification. USB must remain connected.", wraplength=720).pack(anchor="w", pady=(10, 0))
        self.refresh_ports()
        root.after(80, self.poll_events)

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def refresh_ports(self):
        try:
            from serial.tools import list_ports
            previous = self.port.get()
            self.ports = {
                f"{item.device} — {item.description}": item.device
                for item in list_ports.comports()
            }
            values = list(self.ports)
            self.port["values"] = values
            if previous in self.ports:
                self.port.set(previous)
            elif values:
                self.port.set(values[0])
                self.status.set("Ready — select the Arduino port and click Start")
            else:
                self.port.set("")
                self.status.set("No serial ports found — connect Arduino USB and click Refresh")
        except Exception as error:
            self.status.set("Could not list serial ports")
            self.append_log(f"Port detection error: {error}\n")

    def start(self):
        selected = self.ports.get(self.port.get())
        if not selected:
            messagebox.showinfo("Select a port", "Connect the Arduino, click Refresh, and select its port.")
            return
        if self.worker and self.worker.is_alive():
            return
        self.stop.clear()
        self.start_button.configure(state="disabled")
        self.refresh_button.configure(state="disabled")
        self.port.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.set(f"Connecting to {selected}…")
        self.append_log(f"\nStarting on {selected}\n")
        self.worker = threading.Thread(target=run_backend, args=(selected, self.stop, self.events), daemon=True)
        self.worker.start()

    def disconnect(self):
        self.stop.set()
        self.stop_button.configure(state="disabled")
        self.status.set("Stopping and releasing the serial port…")

    def poll_events(self):
        try:
            while True:
                kind, text = self.events.get_nowait()
                if kind == "log":
                    self.append_log(text)
                elif kind == "status":
                    self.status.set(text)
                elif kind == "error":
                    self.append_log(f"ERROR: {text}\nClose Serial Monitor and check the selected port.\n")
                    if not self.closing:
                        messagebox.showerror("Connection error", text + "\n\nClose Serial Monitor and check the selected port.")
                elif kind == "stopped":
                    self.start_button.configure(state="normal")
                    self.refresh_button.configure(state="normal")
                    self.port.configure(state="readonly")
                    self.stop_button.configure(state="disabled")
                    self.status.set("Stopped — you can reconnect or upload firmware")
        except queue.Empty:
            pass
        if self.closing and not (self.worker and self.worker.is_alive()):
            self.root.destroy()
            return
        self.root.after(80, self.poll_events)

    def close(self):
        self.closing = True
        self.disconnect()


def main():
    root = tk.Tk()
    NavigatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
