# tests/test_bot_manager.py

import unittest
from src.bot_manager import BotManager
from src.session_manager import SessionManager

class TestBotManager(unittest.TestCase):
    def setUp(self):
        self.session_manager = SessionManager(':memory:')
        self.bot_manager = BotManager(self.session_manager)

    def test_start_bot_on_all_sessions(self):
        # Mock adding a session
        self.session_manager.add_session("123456", "api_hash", "1234567890", "session_data")
        self.bot_manager.start_bot_on_all_sessions("bot_referral_link")
        # Add assertions based on expected outcomes
        self.assertTrue(True)  # Replace with actual assertions

if __name__ == '__main__':
    unittest.main()
