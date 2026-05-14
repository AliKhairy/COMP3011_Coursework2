import pytest
from src.indexer import InvertedIndex
from src.search import SearchEngine

class TestSearchEngine:
    @pytest.fixture
    def setup_engine(self):
        """
        Creates a real Indexer and SearchEngine for an INTEGRATION TEST.
        Injects a controlled, pre-calculated dictionary into the index.
        """
        indexer = InvertedIndex()
        
        # Manually constructing the index to simulate a post-crawl state
        indexer.index = {
            "good": {
                "http://site.com/1": {"frequency": 1, "positions": [0]},
                "http://site.com/2": {"frequency": 1, "positions": [5]}
            },
            "friends": {
                "http://site.com/2": {"frequency": 1, "positions": [6]},
                "http://site.com/3": {"frequency": 1, "positions": [0]}
            },
            "alone": {
                "http://site.com/4": {"frequency": 5, "positions": [1,2,3,4,5]}
            }
        }
        
        return SearchEngine(indexer)

    def test_find_boolean_and_logic(self, setup_engine):
        """
        Proves that multi-word queries only return URLs containing ALL words.
        'good' and 'friends' only intersect at http://site.com/2.
        """
        results = setup_engine.find_pages("Good Friends") # Note the uppercase to test tokenization too!
        
        assert len(results) == 1
        assert "http://site.com/2" in results

    def test_find_missing_word_fails_gracefully(self, setup_engine):
        """
        Proves the edge case where one word exists, but the other does not.
        A strict Boolean AND must return nothing.
        """
        results = setup_engine.find_pages("good aliens")
        
        assert results == []
        
    def test_find_empty_query(self, setup_engine):
        """
        Proves edge case of an empty query string.
        """
        results = setup_engine.find_pages("   ")
        assert results == []