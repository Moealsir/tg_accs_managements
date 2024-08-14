# src/session_manager.py

import os
import sqlite3
from telethon import TelegramClient, errors, events
import asyncio
import re

class SessionManager:
    def __init__(self, db_path='sessions.db', session_dir='sessions'):
        self.db_path = db_path
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)
        self._create_session_table()
        self.client = None  # Placeholder for the Telegram client

    def _create_session_table(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    api_id TEXT,
                    api_hash TEXT,
                    phone_number TEXT,
                    session_file TEXT
                )
            ''')
            conn.commit()

    async def add_session(self, name, api_id, api_hash, phone_number, code):
        session_file = os.path.join(self.session_dir, f"{phone_number}.session")
        client = TelegramClient(session_file, api_id, api_hash)
        await client.connect()

        try:
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                if not code:
                    code = input(f'Enter the code for {phone_number}: ')
                try:
                    await client.sign_in(phone_number, code)
                except errors.SessionPasswordNeededError:
                    password = input(f'Two-step verification is enabled. Please enter your password for {phone_number}: ')
                    await client.sign_in(password=password)
            
            if os.path.exists(session_file):
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO sessions (name, api_id, api_hash, phone_number, session_file)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, api_id, api_hash, phone_number, session_file))
                    conn.commit()
                print("Session added successfully.")
            else:
                print("Failed to save session data: Session file not created.")

        except errors.AuthRestartError:
            print("Authentication has been restarted. Please check your credentials and try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            await client.disconnect()

    async def get_sessions(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM sessions')
            sessions = c.fetchall()
            result = []
            for s in sessions:
                session_id, name, api_id, api_hash, phone_number, session_file = s
                status = await self.check_session_status(session_file, api_id, api_hash)
                result.append((name, phone_number, status))
            return result


    async def check_session_status(self, session_file, api_id, api_hash):
        client = TelegramClient(session_file, api_id, api_hash)
        try:
            await client.connect()
            if await client.is_user_authorized():
                return 'Active'
            else:
                return 'Inactive'
        except Exception as e:
            print(f"Error checking session status: {e}")
            return 'Error'
        finally:
            await client.disconnect()

    async def remove_session(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT session_file FROM sessions WHERE id=?', (session_id,))
            session_file = c.fetchone()
            if session_file:
                os.remove(session_file[0])
            c.execute('DELETE FROM sessions WHERE id=?', (session_id,))
            conn.commit()

    async def extract_code_from_message(self, message_text):
        patterns = [
            r'login code:\s*(\d+)',
            r'Your login code:\s*([A-Za-z0-9]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                code = match.group(1)
                return code
        return None

    async def start_watching_messages(self, session_file, api_id, api_hash, number):
        self.client = TelegramClient(session_file, api_id, api_hash)
        await self.client.connect()

        async def message_handler(event):
            if event.sender_id == await self.client.get_entity(number):
                code = await self.extract_code_from_message(event.message.text)
                if code:
                    print(f"Extracted login code: {code}")

        self.client.add_event_handler(message_handler, events.NewMessage(incoming=True))
        print("Started watching messages.")
        await self.client.run_until_disconnected()
