import unittest
from catalog import Catalog

class CatalogTests(unittest.TestCase):
    def test_tags_is_copy(self):
        catalog = Catalog(["python"])
        values = catalog.tags()
        values.append("unsafe")
        self.assertEqual(catalog.tags(), ["python"])

if __name__ == "__main__":
    unittest.main()
