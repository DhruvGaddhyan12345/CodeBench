import unittest
from access import is_adult

class AccessTests(unittest.TestCase):
    def test_boundary(self):
        self.assertTrue(is_adult(18))
        self.assertFalse(is_adult(17))

if __name__ == "__main__":
    unittest.main()
