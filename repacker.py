import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import zipfile
import time
from threading import Thread
import subprocess

class FileCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Compressor and Repacker")

        # File selection
        self.file_label = tk.Label(root, text="Select File/Folder:")
        self.file_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Output directory selection
        self.output_label = tk.Label(root, text="Select Output Folder:")
        self.output_label.grid(row=1, column=0, padx=10, pady=10)
        self.output_button = tk.Button(root, text="Browse", command=self.browse_output_directory)
        self.output_button.grid(row=1, column=1, padx=10, pady=10)
        self.output_directory = None

        # Format selection
        self.format_label = tk.Label(root, text="Select Format:")
        self.format_label.grid(row=2, column=0, padx=10, pady=10)
        self.format_var = tk.StringVar(value="zip")
        self.format_menu = tk.OptionMenu(root, self.format_var, "zip", "tar", "gztar", "bztar", "xztar")
        self.format_menu.grid(row=2, column=1, padx=10, pady=10)

        # Chunk size
        self.size_label = tk.Label(root, text="Chunk Size (GB):")
        self.size_label.grid(row=3, column=0, padx=10, pady=10)
        self.size_entry = tk.Entry(root, width=10)
        self.size_entry.grid(row=3, column=1, padx=10, pady=10)
        self.size_entry.insert(0, "1")

        self.size_help = tk.Label(root, text="?", fg="blue", cursor="hand2")
        self.size_help.grid(row=3, column=2, padx=5, pady=10)
        self.size_help.bind("<Button-1>", self.show_chunk_size_help)

        # RAM limit
        self.ram_label = tk.Label(root, text="Max RAM Usage (GB):")
        self.ram_label.grid(row=4, column=0, padx=10, pady=10)
        self.ram_entry = tk.Entry(root, width=10)
        self.ram_entry.grid(row=4, column=1, padx=10, pady=10)
        self.ram_entry.insert(0, "2")

        self.ram_help = tk.Label(root, text="?", fg="blue", cursor="hand2")
        self.ram_help.grid(row=4, column=2, padx=5, pady=10)
        self.ram_help.bind("<Button-1>", self.show_ram_help)

        # Compression button
        self.compress_button = tk.Button(root, text="Compress", command=self.start_compression)
        self.compress_button.grid(row=5, column=0, columnspan=3, pady=20)

        # Installer checkbox
        self.installer_var = tk.BooleanVar()
        self.installer_check = tk.Checkbutton(root, text="Create Installer", variable=self.installer_var)
        self.installer_check.grid(row=6, column=0, columnspan=3)

        self.file_path = None

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, folder_path)
            self.file_path = folder_path

    def browse_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            self.output_button.config(text=f"Save In: {self.output_directory}")

    def show_chunk_size_help(self, event):
        messagebox.showinfo("Chunk Size Help", "Chunk size refers to the size of each part when splitting the file. Larger chunks mean fewer parts, while smaller chunks mean more parts.")

    def show_ram_help(self, event):
        messagebox.showinfo("RAM Usage Help", "Max RAM Usage specifies the maximum amount of RAM the installer can use. Setting this limit helps prevent the installer from using too much memory.")

    def start_compression(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file or folder to compress.")
            return
        if not self.output_directory:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        format_choice = self.format_var.get()
        chunk_size_gb = int(self.size_entry.get())
        chunk_size = chunk_size_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        ram_limit_gb = int(self.ram_entry.get())
        ram_limit = ram_limit_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        create_installer = self.installer_var.get()

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Progress")
        self.progress_label = tk.Label(self.progress_window, text="Starting...")
        self.progress_label.pack(padx=10, pady=10)
        self.progress_bar = ttk.Progressbar(self.progress_window, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)

        self.progress_window.update()

        self.thread = Thread(target=self.perform_compression, args=(self.file_path, format_choice, chunk_size, ram_limit, create_installer))
        self.thread.start()

    def perform_compression(self, file_path, format_choice, chunk_size, ram_limit, create_installer):
        start_time = time.time()
        try:
            base_name = os.path.join(self.output_directory, os.path.basename(file_path))
            output_name = base_name + '.' + format_choice

            if format_choice == 'zip':
                self.compress_to_zip(file_path, output_name)
            else:
                shutil.make_archive(base_name, format_choice, file_path if os.path.isdir(file_path) else os.path.dirname(file_path), os.path.basename(file_path))

            if format_choice != 'zip':
                self.split_file(output_name, chunk_size)

            if create_installer:
                self.create_installer(base_name, output_name, ram_limit)

            elapsed_time = time.time() - start_time
            self.progress_label.config(text=f"Operation completed in {elapsed_time:.2f} seconds.")
            self.progress_bar['value'] = 100
            self.progress_window.update()

        except Exception as e:
            self.progress_label.config(text=f"An error occurred: {str(e)}")
            self.progress_bar['value'] = 0
            self.progress_window.update()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            self.progress_window.after(3000, self.progress_window.destroy)

    def compress_to_zip(self, file_path, output_name):
        with zipfile.ZipFile(output_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        self.progress_label.config(text=f"Compressing file: {file_full_path}")
                        self.progress_window.update()
                        zipf.write(file_full_path, os.path.relpath(file_full_path, os.path.dirname(file_path)))
            else:
                zipf.write(file_path, os.path.basename(file_path))

    def split_file(self, file_path, chunk_size):
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as src_file:
            chunk_number = 0
            while True:
                chunk = src_file.read(chunk_size)
                if not chunk:
                    break
                with open(f"{file_path}.part{chunk_number:03d}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                chunk_number += 1
        os.remove(file_path)

    def create_installer(self, base_name, archive_name, ram_limit):
        installer_script = f"""
        @echo off
        setlocal
        set ARCHIVE_NAME={archive_name}
        set OUTPUT_DIR=%~dp0output
        mkdir %OUTPUT_DIR%
        copy /b {archive_name}.part* {archive_name}
        tar -xf {archive_name} -C %OUTPUT_DIR%
        echo Decompression complete.
        pause
        endlocal
        """
        installer_path = os.path.join(self.output_directory, "installer.bat")
        with open(installer_path, 'w') as script_file:
            script_file.write(installer_script)
        self.progress_label.config(text="Running installer...")
        self.progress_window.update()
        self.run_installer(installer_path)

    def run_installer(self, installer_path):
        subprocess.Popen(installer_path, shell=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCompressorGUI(root)
    root.mainloop()
