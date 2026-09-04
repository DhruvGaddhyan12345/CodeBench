import unittest
from numbers import is_even

class NumberTests(unittest.TestCase):
    def test_even(self):
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(3))

if __name__ == "__main__":
    unittest.main()
