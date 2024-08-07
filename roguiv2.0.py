import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Button, Controller
from pynput import keyboard
from threading import Thread
import time

class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RoGui Autoclicker  MADE BY suiyang12 (steve)")

        self.mouse = Controller()
        self.clicking = False
        self.afk_mode = False

        self.create_widgets()
        self.setup_hotkeys()
        self.root.mainloop()

    def create_widgets(self):
        # Interval input
        ttk.Label(self.root, text="Click Interval (ms):").grid(row=0, column=0, padx=10, pady=5)
        self.interval_entry = ttk.Entry(self.root)
        self.interval_entry.grid(row=0, column=1, padx=10, pady=5)
        self.interval_entry.insert(0, "1000")  # Default to 1000 ms

        # Mouse button selection
        ttk.Label(self.root, text="Mouse Button:").grid(row=1, column=0, padx=10, pady=5)
        self.button_choice = ttk.Combobox(self.root, values=["Left", "Right"])
        self.button_choice.grid(row=1, column=1, padx=10, pady=5)
        self.button_choice.current(0)  # Default to Left button

        # Enable/disable autoclicker buttons
        self.enable_button = ttk.Button(self.root, text="Enable Autoclicker", command=self.enable_clicking)
        self.enable_button.grid(row=2, column=0, padx=10, pady=10)

        self.disable_button = ttk.Button(self.root, text="Disable Autoclicker", command=self.disable_clicking)
        self.disable_button.grid(row=2, column=1, padx=10, pady=10)

        # Enable/disable AFK mode buttons
        self.enable_afk_button = ttk.Button(self.root, text="Enable AFK Mode", command=self.enable_afk_mode)
        self.enable_afk_button.grid(row=3, column=0, padx=10, pady=10)

        self.disable_afk_button = ttk.Button(self.root, text="Disable AFK Mode", command=self.disable_afk_mode)
        self.disable_afk_button.grid(row=3, column=1, padx=10, pady=10)

    def enable_clicking(self):
        try:
            self.interval = int(self.interval_entry.get()) / 1000.0  # Convert ms to seconds
            self.button = Button.left if self.button_choice.get() == "Left" else Button.right
            self.clicking = True
            self.start_clicking()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the interval.")

    def disable_clicking(self):
        self.clicking = False

    def enable_afk_mode(self):
        self.afk_mode = True
        self.root.withdraw()  # Hide the GUI window

    def disable_afk_mode(self):
        self.afk_mode = False
        self.root.deiconify()  # Show the GUI window

    def start_clicking(self):
        def click_loop():
            while self.clicking:
                self.mouse.click(self.button)
                time.sleep(self.interval)

        click_thread = Thread(target=click_loop)
        click_thread.start()

    def setup_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f1:
                    self.enable_clicking()
                elif key == keyboard.Key.f3:
                    self.enable_afk_mode()
                elif key == keyboard.Key.f5:
                    self.disable_afk_mode()
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

if __name__ == "__main__":
    AutoClicker()
