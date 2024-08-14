# tests/test_session_manager.py

import unittest
from src.session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.session_manager = SessionManager(':memory:')  # Use in-memory DB for testing

    def test_add_and_get_session(self):
        self.session_manager.add_session("123456", "api_hash", "1234567890", "session_data")
        sessions = self.session_manager.get_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0][1], "123456")

    def test_remove_session(self):
        self.session_manager.add_session("123456", "api_hash", "1234567890", "session_data")
        self.session_manager.remove_session(1)
        sessions = self.session_manager.get_sessions()
        self.assertEqual(len(sessions), 0)

if __name__ == '__main__':
    unittest.main()
