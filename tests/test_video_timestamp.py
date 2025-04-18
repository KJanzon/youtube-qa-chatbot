import unittest
from utils.time import timestamp_to_seconds


class TestTimestampConversion(unittest.TestCase):
    def test_valid_timestamp(self):
        self.assertEqual(timestamp_to_seconds("00:00:00"), 0)
        self.assertEqual(timestamp_to_seconds("00:01:30"), 90)
        self.assertEqual(timestamp_to_seconds("01:00:00"), 3600)
        self.assertEqual(timestamp_to_seconds("00:10:05"), 605)

    def test_invalid_format(self):
        self.assertEqual(timestamp_to_seconds("bad input"), 0)
        self.assertEqual(timestamp_to_seconds(""), 0)


class TestDocumentMetadata(unittest.TestCase):
    def test_timestamp_present_in_metadata(self):
        # Simulate a source doc from LangChain
        mock_doc = {
            "metadata": {"timestamp": "00:02:10"},
            "page_content": "Some text about loops"
        }
        ts = mock_doc["metadata"].get("timestamp", "00:00:00")
        self.assertEqual(timestamp_to_seconds(ts), 130)


if __name__ == '__main__':
    unittest.main()
