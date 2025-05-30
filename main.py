import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import random

class NuclearReactor:
    def __init__(self):
        self.neutrons = 100
        self.u235_atoms = 1e6
        self.temperature = 300
        self.control_rod_level = 50
        self.power_output = 0
        self.scram_triggered = False
        self.time = 0
        self.k_eff = 1.0
        self.running = False

        self.time_log = []
        self.temp_log = []
        self.power_log = []

    def insert_control_rods(self, amount):
        self.control_rod_level = min(100, self.control_rod_level + amount)

    def withdraw_control_rods(self, amount):
        self.control_rod_level = max(0, self.control_rod_level - amount)

    def calculate_k_eff(self):
        return max(0.1, 1.2 - self.control_rod_level / 100)

    def simulate_step(self, dt=1):
        if self.scram_triggered:
            self.k_eff = 0.5
        else:
            self.k_eff = self.calculate_k_eff()

        new_neutrons = self.neutrons * self.k_eff
        fissions = min(self.u235_atoms, new_neutrons * 0.01)
        self.u235_atoms -= fissions
        self.neutrons = new_neutrons
        energy_per_fission = 200e-6
        self.power_output = fissions * energy_per_fission
        self.temperature += 0.01 * self.power_output - 0.5 * (self.temperature - 300) * dt

        if self.temperature > 1000:
            self.scram_triggered = True

        self.time += dt
        self.time_log.append(self.time)
        self.temp_log.append(self.temperature)
        self.power_log.append(self.power_output)


class ReactorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚛️ Nuclear Reactor Simulator")

        self.reactor = NuclearReactor()
        self.running = False

        # Layout
        self.build_controls()
        self.build_charts()
        self.build_core_visual()

        self.update_gui()
        self.update_core_visual()

    def build_controls(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(control_frame, text="Control Rod Level:").pack(side=tk.LEFT, padx=5)
        self.rod_label = ttk.Label(control_frame, text="50%")
        self.rod_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="⬆ Withdraw Rods", command=self.withdraw_rods).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⬇ Insert Rods", command=self.insert_rods).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="▶ Run", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏹ Stop", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)

    def build_charts(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5,4), dpi=100)
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def build_core_visual(self):
        self.core_canvas = tk.Canvas(self.root, width=300, height=300, bg='black')
        self.core_canvas.pack(side=tk.RIGHT, padx=10)

    def update_core_visual(self):
        self.core_canvas.delete("all")
        temp = self.reactor.temperature
        color = self.temperature_to_color(temp)

        for i in range(5):
            for j in range(5):
                x0, y0 = 20 + j*50, 20 + i*50
                x1, y1 = x0 + 40, y0 + 40
                self.core_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="grey")

    def temperature_to_color(self, temp):
        if temp < 400:
            return "#2244ff"
        elif temp < 600:
            return "#44ddff"
        elif temp < 800:
            return "#ffaa00"
        elif temp < 1000:
            return "#ff4400"
        else:
            return "#ff0000"

    def update_gui(self):
        self.rod_label.config(text=f"{self.reactor.control_rod_level}%")
        self.update_core_visual()

        # Update charts
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_title("Temperature (K)")
        self.ax2.set_title("Power Output (MW)")
        self.ax1.plot(self.reactor.time_log, self.reactor.temp_log, color='red')
        self.ax2.plot(self.reactor.time_log, self.reactor.power_log, color='blue')
        self.canvas.draw()

        if self.running:
            self.root.after(500, self.update_gui)

    def insert_rods(self):
        self.reactor.insert_control_rods(10)

    def withdraw_rods(self):
        self.reactor.withdraw_control_rods(10)

    def start_simulation(self):
        if not self.running:
            self.running = True
            self.reactor.running = True
            threading.Thread(target=self.simulation_loop, daemon=True).start()
            self.update_gui()

    def stop_simulation(self):
        self.running = False
        self.reactor.running = False

    def simulation_loop(self):
        while self.running:
            self.reactor.simulate_step()
            time.sleep(0.5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReactorGUI(root)
    root.mainloop()
