"""Optional Streamlit tests: install requirements.txt to run these."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit not installed")
class DashboardTests(unittest.TestCase):
    def test_local_demo_and_authorization(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
        self.assertEqual(len(app.exception), 0)
        app.button[1].click().run()
        self.assertTrue(app.session_state["result"].demo)
        self.assertEqual(len(app.exception), 0)
        with patch("cybershield.scanner.scan") as scanner:
            app.button[0].click().run()
            scanner.assert_not_called()
            self.assertGreater(len(app.error), 0)
            self.assertNotIn("result", app.session_state)

    def test_demo_only_app(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "demo_app.py")).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.session_state["result"].demo)
