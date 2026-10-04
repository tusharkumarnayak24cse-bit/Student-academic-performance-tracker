import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
class ScreenTests(unittest.TestCase):
 def test_screens(self):
  app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
  self.assertFalse(app.exception)
  for page in ['Trends & prediction','Target planner','Manage data','Project guide','Overview']:
   app.sidebar.radio[0].set_value(page).run(timeout=30)
   self.assertFalse(app.exception, page)
