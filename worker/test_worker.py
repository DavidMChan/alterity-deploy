import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

# Mock modules before import
sys.modules['database'] = MagicMock()
sys.modules['llm'] = MagicMock()

from modules.demographic_forcing import run_demographic_forcing
from modules.matcher import matcher
from modules.dynamic_labeler import labeler

class TestWorkerModules(unittest.TestCase):

    @patch('modules.demographic_forcing.chat_completion')
    def test_demographic_forcing(self, mock_chat):
        print("\nTesting Demographic Forcing...")
        mock_chat.return_value = "As a Republican..."
        response = run_demographic_forcing("Question", {"political_party": "Republican"})
        self.assertIn("Republican", response)
        mock_chat.assert_called_once()

    def test_matcher_logic(self):
        print("\nTesting Matcher Logic...")
        targets = [{"id": 1, "age": "30", "political_party": "Democrat"}]
        # Mock candidates
        candidates = [{"id": 101, "demographics": {"age": "30", "political_party": "Democrat"}, "custom_tags": {}}]
        matches = matcher.perform_matching(targets, candidates)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][0]['id'], 1)
        self.assertEqual(matches[0][1]['id'], 101)

    @patch('modules.dynamic_labeler.chat_completion')
    def test_labeler(self, mock_chat):
        print("\nTesting Labeler...")
        mock_chat.return_value = "Yes"
        result = labeler.check_trait("content", "owns_gov")
        self.assertEqual(result, "Yes")

if __name__ == "__main__":
    unittest.main()
