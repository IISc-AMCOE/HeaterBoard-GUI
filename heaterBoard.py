from serialProtocol import SerialProtocol
import tkinter as tk
from tkinter import ttk
import threading
import time

class HeaterBoard:
    def __init__(self, port="COM8"):
        self.serial_model = SerialProtocol(port=port, baudrate=115200, timeout=1)

    def setHeaterPowers(self, ch8, ch7, ch6, ch5, ch4, ch3, ch2, ch1):
        command = f"8,{ch8},{ch7},{ch6},{ch5},{ch4},{ch3},{ch2},{ch1}"
        future = self.serial_model.send_command_async(command)
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        try:
            response = future.result()
        except Exception as e:
            print(f"Error in async response: {e}")

    def stopHeaters(self):
        command = "8,1,1,1,1,1,1,1,1"
        future = self.serial_model.send_command_async(command)
        future.add_done_callback(self.handle_response)
        print("Heater stopped")

def clamp(val):
    try:
        return max(1, min(99, int(val)))
    except:
        return 1

class HeaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Heater Board Control")
        self.running = False

        # COM port selection
        ttk.Label(root, text="COM Port:").grid(row=0, column=0, sticky="w")
        self.com_var = tk.StringVar(value="COM8")
        self.com_entry = ttk.Entry(root, textvariable=self.com_var, width=10)
        self.com_entry.grid(row=0, column=1, sticky="w")

        # Heater controls
        self.vars = {
            "left_inner": tk.IntVar(value=1),
            "left_outer": tk.IntVar(value=1),
            "back_inner": tk.IntVar(value=1),
            "back_outer": tk.IntVar(value=1),
            "right_inner": tk.IntVar(value=1),
            "right_outer": tk.IntVar(value=1),
            "front_inner": tk.IntVar(value=1),
            "front_outer": tk.IntVar(value=1),
        }

        row = 1
        for name in self.vars:
            ttk.Label(root, text=name.replace("_", " ").title()).grid(row=row, column=0, sticky="w")
            ttk.Spinbox(root, from_=1, to=99, textvariable=self.vars[name], width=5).grid(row=row, column=1)
            row += 1

        self.start_btn = ttk.Button(root, text="Start", command=self.start)
        self.start_btn.grid(row=row, column=0, pady=10)
        self.stop_btn = ttk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=row, column=1, pady=10)

        self.heater_board = None

    def start(self):
        port = self.com_var.get()
        self.heater_board = HeaterBoard(port=port)
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.send_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        if self.heater_board:
            self.heater_board.stopHeaters()

    def send_loop(self):
        while self.running:
            self.heater_board.setHeaterPowers(
                clamp(self.vars["left_inner"].get()),
                clamp(self.vars["left_outer"].get()),
                clamp(self.vars["back_inner"].get()),
                clamp(self.vars["back_outer"].get()),
                clamp(self.vars["right_inner"].get()),
                clamp(self.vars["right_outer"].get()),
                clamp(self.vars["front_inner"].get()),
                clamp(self.vars["front_outer"].get()),
            )
            time.sleep(0.2)

if __name__ == "__main__":
    root = tk.Tk()
    app = HeaterGUI(root)
    root.mainloop()