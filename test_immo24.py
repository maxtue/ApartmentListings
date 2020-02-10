import unittest
import immo24


class TestNameIrrelevant(unittest.TestCase):
    def test_get_data(self):
        self.assertEqual(immo24.Immo24scrape.get_data(), 15)


if __name__ == "__main__":
    unittest.main()
