import unittest
from main import (
    preprocess_text,
    find_keywords,
    generate_summary,
    determine_length_category,
)

class TestPDFProcessor(unittest.TestCase):

    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "Hello, World!"
        expected = ['hello', 'world']
        self.assertEqual(preprocess_text(text), expected)

    def test_find_keywords_basic(self):
        """Test keyword extraction without specific terms."""
        text = "This is a test. Test the keyword function. Test test test."
        expected = ['test', 'function', 'the', 'is', 'a']  # Adjust if your function behaves differently
        actual_keywords = find_keywords(text, limit=5)
        print("Actual Keywords:", actual_keywords)  # Debugging line to see the actual output
        self.assertCountEqual(actual_keywords, expected)

    def test_determine_length_category_short(self):
        """Test document length classification for short documents."""
        self.assertEqual(determine_length_category("Short text."), 'short')

    def test_determine_length_category_medium(self):
        """Test document length classification for medium-length documents."""
        text = "This is a medium-length text. " * 20  # Approx. 100 words
        self.assertEqual(determine_length_category(text), 'medium')

    def test_determine_length_category_long(self):
        """Test document length classification for long documents."""
        text = "This is a long document. " * 100  # Approx. 500 words
        self.assertEqual(determine_length_category(text), 'long')

    def test_generate_summary_short(self):
        """Test summary generation for short documents."""
        text = "This is a short sentence."
        expected = "This is a short sentence."  # Matches expected output
        self.assertEqual(generate_summary(text, 'short'), expected)

    def test_generate_summary_medium(self):
        """Test summary generation for medium-length documents."""
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        expected = "Sentence one. Sentence two. Sentence three."  # No extra period
        self.assertEqual(generate_summary(text, 'medium'), expected)

    def test_generate_summary_long(self):
        """Test summary generation for long documents."""
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
        expected = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
        self.assertEqual(generate_summary(text, 'long'), expected)

if _name_ == "_main_":
    unittest.main()