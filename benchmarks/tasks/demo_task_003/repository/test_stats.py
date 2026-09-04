import unittest
from stats import average

class StatsTests(unittest.TestCase):
    def test_average_empty(self):
        self.assertEqual(average([]), 0)

if __name__ == "__main__":
    unittest.main()
