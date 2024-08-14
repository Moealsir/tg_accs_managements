# src/gui/dashboard.py

import sys
import os
import tkinter as tk
from tkinter import ttk

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from session_gui import SessionGUI

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Telegram Session Dashboard")

        # Center the window
        self.center_window(800, 600)  # Set desired width and height

        self.session_gui = SessionGUI(self.root)
        self.session_gui.load_sessions()  # Ensure sessions are loaded and statuses are checked

        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)
        
        session_tab = ttk.Frame(tab_control)

        tab_control.add(session_tab, text='Sessions')
        tab_control.pack(expand=1, fill='both')
        

        self.session_gui.create_widgets(session_tab)

    def center_window(self, width, height):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position x, y to place the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the dimensions and position of the window
        self.root.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
