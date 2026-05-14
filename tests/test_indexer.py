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

    def test_save_and_load_file_io(self, indexer, tmp_path):
        """
        Proves the indexer can serialize its data to JSON and save it to the OS.
        Uses pytest's tmp_path fixture to avoid creating real files.
        """
        # 1. Setup: Add some dummy data to the index
        indexer.add_document("http://io-test.com", "save me")
        
        # 2. Create a temporary, isolated file path
        test_file = tmp_path / "test_data" / "test_index.json"
        
        # 3. Execute the save
        indexer.save_to_file(str(test_file))
        
        # 4. Assert the file actually generated on the (temporary) hard drive
        assert test_file.exists()
        
        # 5. Create a completely blank, secondary indexer
        new_indexer = InvertedIndex()
        
        # 6. Load the temporary file into the new indexer
        new_indexer.load_from_file(str(test_file))
        
        # 7. Assert the data survived the round trip!
        assert "save" in new_indexer.index
        assert "me" in new_indexer.index
        assert len(new_indexer.total_urls) == 1

    def test_load_file_not_found_graceful_fail(self, indexer, capsys):
        """
        Proves the system doesn't crash if the user types 'load' before 'build'.
        """
        # Attempt to load a file that mathematically cannot exist
        indexer.load_from_file("path/to/absolute/nowhere.json")
        
        # Capture the terminal output to prove it printed an error instead of crashing
        captured = capsys.readouterr()
        assert "Error: Could not find index file" in captured.out