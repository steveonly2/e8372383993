import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading
import json
import os

DATA_FILE = "autopinger_data.json"

class AutoPingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPinger")

        self.webhook_url = None
        self.user_ids = []
        self.custom_message = "@everyone This is a ping from the webhook!"
        self.delay_seconds = 2
        self.repeat_pinging = tk.BooleanVar()
        self.is_pinging = False

        # Load saved data
        self.load_data()

        # Layout
        self.create_widgets()
        self.layout_widgets()

        # Hotkeys
        self.setup_hotkeys()

        # Show guide on startup
        self.show_guide()

    def create_widgets(self):
        # AutoPinger Button
        self.ping_button = tk.Button(self.root, text="AutoPinger", command=self.start_pinging)

        # Input Webhook
        self.webhook_label = tk.Label(self.root, text="Webhook URL:")
        self.webhook_entry = tk.Entry(self.root, width=50)
        self.webhook_entry.insert(0, self.webhook_url or "")

        # Input User IDs
        self.user_label = tk.Label(self.root, text="Specific User IDs (comma separated, optional):")
        self.user_entry = tk.Entry(self.root, width=50)
        self.user_entry.insert(0, ", ".join(self.user_ids) if self.user_ids else "")

        # Custom Message
        self.message_label = tk.Label(self.root, text="Custom Message:")
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.insert(0, self.custom_message)

        # Repeat Pinging Checkbox
        self.repeat_check = tk.Checkbutton(self.root, text="Enable Repeated Pinging", variable=self.repeat_pinging)

        # Delay Input
        self.delay_label = tk.Label(self.root, text="Delay between pings (seconds):")
        self.delay_entry = tk.Entry(self.root, width=10)
        self.delay_entry.insert(0, str(self.delay_seconds))

    def layout_widgets(self):
        # Layout all widgets
        self.webhook_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.webhook_entry.grid(row=0, column=1, padx=10, pady=5)

        self.user_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.user_entry.grid(row=1, column=1, padx=10, pady=5)

        self.message_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.message_entry.grid(row=2, column=1, padx=10, pady=5)

        self.repeat_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.delay_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.delay_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.ping_button.grid(row=5, column=0, columnspan=2, pady=10)

    def setup_hotkeys(self):
        self.root.bind('<F3>', self.toggle_pinging)  # F3 to start/stop pinging
        self.root.bind('<F10>', lambda event: self.root.quit())  # F10 to quit

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.webhook_url = data.get("webhook_url")
                self.user_ids = data.get("user_ids", [])
                self.custom_message = data.get("custom_message", self.custom_message)
                self.delay_seconds = data.get("delay_seconds", self.delay_seconds)

    def save_data(self):
        data = {
            "webhook_url": self.webhook_url,
            "user_ids": self.user_ids,
            "custom_message": self.custom_message,
            "delay_seconds": self.delay_seconds,
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

    def show_guide(self, event=None):
        guide_message = (
            "Welcome to AutoPinger!\n\n"
            "Please follow these steps:\n"
            "1. Enter the Webhook URL.\n"
            "2. Optionally, enter User IDs to ping specific users (comma separated).\n"
            "3. Customize the message if needed.\n"
            "4. Enable repeated pinging and set the delay if required.\n\n"
            "Hotkeys:\n"
            "- F3: Start/Stop pinging\n"
            "- F10: Quit the application\n\n"
            "We abide by the rules and regulations of Discord. This program is solely made for experimental purposes. "
            "Spamming or using this software for unethical uses is PURELY AT YOUR OWN RISK.\n\n"
            "Click 'AutoPinger' to start or stop the pinging process."
        )
        messagebox.showinfo("AutoPinger", guide_message)

    def start_pinging(self):
        self.webhook_url = self.webhook_entry.get()
        if not self.webhook_url:
            messagebox.showerror("Error", "Please enter a webhook URL.")
            return

        user_ids = self.user_entry.get().strip()
        self.user_ids = [user_id.strip() for user_id in user_ids.split(",") if user_id.strip()]
        self.custom_message = self.message_entry.get() or self.custom_message
        try:
            self.delay_seconds = int(self.delay_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the delay.")
            return
        
        # Save data for next time
        self.save_data()

        if self.is_pinging:
            self.is_pinging = False
            self.ping_button.config(text="AutoPinger")
        else:
            self.is_pinging = True
            self.ping_button.config(text="Stop Pinging")
            self.ping_thread = threading.Thread(target=self.ping_everyone)
            self.ping_thread.start()

    def toggle_pinging(self, event=None):
        self.start_pinging()

    def ping_everyone(self):
        while self.is_pinging:
            try:
                if self.user_ids:
                    mentions = " ".join(f"<@{user_id}>" for user_id in self.user_ids)
                    content = f"{mentions} {self.custom_message}"
                else:
                    content = self.custom_message

                data = {
                    "content": content,
                    "username": "Ping Bot",
                }

                response = requests.post(self.webhook_url, json=data)
                if response.status_code == 204:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {response.status_code}")

                if self.repeat_pinging.get():
                    time.sleep(self.delay_seconds)
                else:
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoPingerApp(root)
    root.mainloop()
