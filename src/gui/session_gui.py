import tkinter as tk
from tkinter import simpledialog, messagebox
from session_manager import SessionManager
import asyncio
import threading
import sqlite3
import re
from telethon import TelegramClient, events  # Import missing modules

class SessionGUI:
    def __init__(self, root):
        self.root = root
        self.session_manager = SessionManager()
        self.session_listbox = None

    def create_widgets(self, parent):
        self.session_listbox = tk.Listbox(parent, selectmode=tk.SINGLE)
        self.session_listbox.pack(fill=tk.BOTH, expand=1)

        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X)

        add_btn = tk.Button(btn_frame, text="Add Session", command=self.add_session)
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        remove_btn = tk.Button(btn_frame, text="Remove Session", command=self.remove_session)
        remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        status_btn = tk.Button(btn_frame, text="Check Status", command=self.check_status)
        status_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        fetch_code_btn = tk.Button(btn_frame, text="Get Code", command=self.fetch_code_from_number)
        fetch_code_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self.load_sessions()

    def load_sessions(self):
        def run_async():
            async def load():
                sessions = await self.session_manager.get_sessions()
                return sessions

            def update_listbox(sessions):
                self.session_listbox.delete(0, tk.END)
                for session in sessions:
                    name, phone_number, status = session
                    status_color = 'green' if status == 'Active' else 'red'
                    self.session_listbox.insert(tk.END, f"{name} - {phone_number} - {status}")
                    self.session_listbox.itemconfig(tk.END, {'bg': status_color})

            sessions = asyncio.run(load())
            self.root.after(0, update_listbox, sessions)

        threading.Thread(target=run_async).start()


    def add_session(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Session")

        # Center the add session window using the `center_window` method from this class
        self.center_window(add_window, 300, 300)  # Pass the window and dimensions

        tk.Label(add_window, text="Session Name").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="API ID").pack(pady=5)
        api_id_entry = tk.Entry(add_window)
        api_id_entry.pack(pady=5)

        tk.Label(add_window, text="API Hash").pack(pady=5)
        api_hash_entry = tk.Entry(add_window)
        api_hash_entry.pack(pady=5)

        tk.Label(add_window, text="Phone Number").pack(pady=5)
        phone_entry = tk.Entry(add_window)
        phone_entry.pack(pady=5)

        def save_session():
            name = name_entry.get()
            api_id = api_id_entry.get()
            api_hash = api_hash_entry.get()
            phone_number = phone_entry.get()

            def run_async():
                asyncio.run(self.session_manager.add_session(name, api_id, api_hash, phone_number, ''))
                self.load_sessions()

            threading.Thread(target=run_async).start()
            add_window.destroy()

        save_btn = tk.Button(add_window, text="Save", command=save_session)
        save_btn.pack(pady=10)


    def center_window(self, window, width, height):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position x, y to place the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the dimensions and position of the window
        window.geometry(f'{width}x{height}+{x}+{y}')

    def remove_session(self):
        selected = self.session_listbox.curselection()
        if selected:
            session_id = selected[0] + 1  # Adjust if necessary based on your session ID logic
            def run_async():
                asyncio.run(self.session_manager.remove_session(session_id))
                self.load_sessions()
            threading.Thread(target=run_async).start()
        else:
            messagebox.showwarning("No selection", "Please select a session to remove.")

    def check_status(self):
        selected = self.session_listbox.curselection()
        if selected:
            session_id = selected[0] + 1  # Adjust if necessary based on your session ID logic
            
            def run_async():
                # Fetch session details from the database
                async def fetch_session_details():
                    with sqlite3.connect(self.session_manager.db_path) as conn:
                        c = conn.cursor()
                        c.execute('SELECT session_file, api_id, api_hash FROM sessions WHERE id=?', (session_id,))
                        session = c.fetchone()
                        return session

                session = asyncio.run(fetch_session_details())
                if session:
                    session_file, api_id, api_hash = session
                    status = asyncio.run(self.session_manager.check_session_status(session_file, api_id, api_hash))
                    messagebox.showinfo("Session Status", f"Session {session_id} status: {status}")
                else:
                    messagebox.showwarning("Session Not Found", "Session ID not found in the database.")

            threading.Thread(target=run_async).start()
        else:
            messagebox.showwarning("No selection", "Please select a session to check status.")

    def fetch_code_from_number(self):
        selected = self.session_listbox.curselection()
        if selected:
            session_id = selected[0] + 1  # Adjust if necessary based on your session ID logic

            def run_async():
                async def fetch_session_details():
                    with sqlite3.connect(self.session_manager.db_path) as conn:
                        c = conn.cursor()
                        c.execute('SELECT session_file, api_id, api_hash FROM sessions WHERE id=?', (session_id,))
                        session = c.fetchone()
                        return session

                session = asyncio.run(fetch_session_details())
                if session:
                    session_file, api_id, api_hash = session

                    async def watch_messages():
                        client = TelegramClient(session_file, api_id, api_hash)

                        @client.on(events.NewMessage(incoming=True))
                        async def handle_incoming_message(event):
                            # Check if the sender is the specific phone number
                            if event.message.sender_id:
                                sender = await client.get_entity(event.message.sender_id)
                                if sender.phone == '+24777':
                                    message_text = event.message.text

                                    # Regular expression patterns for extracting the login code
                                    patterns = [
                                        r'login code:\s*(\d+)',  # For message type 2
                                        r'Your login code:\s*([A-Za-z0-9]+)',  # For message type 1 (alphanumeric codes)
                                    ]

                                    # Check each pattern and extract the code
                                    for pattern in patterns:
                                        match = re.search(pattern, message_text, re.IGNORECASE)
                                        if match:
                                            code = match.group(1)
                                            
                                            # Show the extracted code in a dialog
                                            self.show_code_dialog(code)
                                            
                                            await client.disconnect()  # Stop after finding the code
                                            return

                        await client.connect()
                        print("Started watching messages.")
                        await client.run_until_disconnected()

                    threading.Thread(target=lambda: asyncio.run(watch_messages())).start()
                else:
                    messagebox.showwarning("Session Not Found", "Session ID not found in the database.")

            threading.Thread(target=run_async).start()
        else:
            messagebox.showwarning("No selection", "Please select a session to fetch code.")

    def show_code_dialog(self, code):
        messagebox.showinfo("Login Code", f"Extracted code: {code}")
        # Ask the user to enter the password if needed
        password = simpledialog.askstring("Password", "Enter your password for two-step verification:")
        if password:
            # Handle the password (e.g., send it to the server or use it in further authentication)
            print(f"Password entered: {password}")
            # You may want to include further handling of the password, such as sending it to the server
