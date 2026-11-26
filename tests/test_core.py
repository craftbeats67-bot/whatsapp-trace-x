import unittest, tempfile
from pathlib import Path
import core
class CoreTests(unittest.TestCase):
 def test_phone_format(self):
  self.assertTrue(core.validate_phone('+91','9876543210')[0])
  self.assertFalse(core.validate_phone('91','9876543210')[0])
 def test_analysis(self):
  r=core.analyze_text('Please pay me ₹500 or I will leak your photos')
  self.assertEqual(len(r['flagged_lines']),1)
 def test_link_inspection_does_not_fetch(self):
  r=core.inspect_invitation('Join https://example.com/invite/abc')
  self.assertEqual(r['urls'][0]['host'],'example.com')
if __name__=='__main__': unittest.main()
