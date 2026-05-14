import pytest
import os
from src.indexer import InvertedIndex

class TestInvertedIndex:
    @pytest.fixture
    def indexer(self):
        """Provides a fresh InvertedIndex instance for each test."""
        return InvertedIndex()

    def test_tokenize_cleans_text_properly(self, indexer):
        """
        Proves the indexer handles case insensitivity and strips punctuation.
        This is a critical edge case for web text.
        """
        raw_text = "Hello!!   This is a TEST, a messy test... \n \t right?"
        expected_tokens = ["hello", "this", "is", "a", "test", "a", "messy", "test", "right"]
        
        actual_tokens = indexer._tokenize(raw_text)
        
        assert actual_tokens == expected_tokens

    def test_add_document_stores_statistics(self, indexer):
        """
        Proves the index correctly maps words to URLs and accurately 
        tracks both frequency and positional data.
        """
        url = "http://test.com"
        # 'apple' appears at index 0 and 2. 'banana' at index 1.
        text = "Apple banana APPLE." 
        
        indexer.add_document(url, text)
        
        # Verify the structure and statistics for "apple"
        assert "apple" in indexer.index
        assert url in indexer.index["apple"]
        assert indexer.index["apple"][url]["frequency"] == 2
        assert indexer.index["apple"][url]["positions"] == [0, 2]
        
        # Verify the structure and statistics for "banana"
        assert indexer.index["banana"][url]["frequency"] == 1
        assert indexer.index["banana"][url]["positions"] == [1]