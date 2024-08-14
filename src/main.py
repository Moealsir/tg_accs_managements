# src/main.py

import asyncio
from session_manager import SessionManager

def main():
    print("Welcome to the Multi-Telegram Session Dashboard")

    # Initialize session manager
    session_manager = SessionManager()

    # CLI Options
    while True:
        print("\nOptions:")
        print("1. Add Session")
        print("2. View Sessions")
        print("3. Remove Session")
        print("4. Check Session Status")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            name = input("Enter Session Name: ")
            api_id = input("Enter API ID: ")
            api_hash = input("Enter API Hash: ")
            phone_number = input("Enter Phone Number: ")
            asyncio.run(session_manager.add_session(name, api_id, api_hash, phone_number, ''))
        elif choice == "2":
            sessions = asyncio.run(session_manager.get_sessions())
            print("Sessions:")
            for session in sessions:
                print(session)
        elif choice == "3":
            session_id = input("Enter Session ID to remove: ")
            asyncio.run(session_manager.remove_session(session_id))
        elif choice == "4":
            sessions = asyncio.run(session_manager.get_sessions())
            print("Checking status for all sessions:")
            for session in sessions:
                name, phone_number, status = session
                print(f"Session Name: {name}, Phone Number: {phone_number}, Status: {status}")
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
