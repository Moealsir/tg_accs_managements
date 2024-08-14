# test_session.py

from telethon import TelegramClient, errors

async def test_session():
    api_id = '20538654'
    api_hash = '9ba174bab918c17cfba4c4619f2e0ac6'
    phone_number = '97439900342'

    client = TelegramClient(phone_number, api_id, api_hash)
    await client.connect()

    try:
        if not await client.is_user_authorized():
            print("Not authorized, sending code request...")
            await client.send_code_request(phone_number)
            code = input(f'Enter the code for {phone_number}: ')
            
            try:
                await client.sign_in(phone_number, code)
            except errors.SessionPasswordNeededError:
                password = input(f'Two-step verification is enabled. Please enter your password for {phone_number}: ')
                await client.sign_in(password=password)
            except errors.AuthRestartError:
                print("Authentication has been restarted. Please check your credentials and try again.")
                return
        
        # Check if the client is now authorized
        if not await client.is_user_authorized():
            print("Failed to authorize the client.")
            return

        print("Client authorized. Saving session...")
        session_str = client.session.save()
        print(f"Session string: {session_str}")

        # Test client connection
        if client.is_connected():
            print("Client is connected.")
        else:
            print("Client is not connected.")

    except errors.AuthRestartError:
        print("Authentication has been restarted. Please check your credentials and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        await client.disconnect()

# Run the test function
import asyncio
asyncio.run(test_session())
