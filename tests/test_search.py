import pytest
from src.indexer import InvertedIndex
from src.search import SearchEngine

class TestSearchEngine:
    @pytest.fixture
    def setup_engine(self):
        """
        Creates a real Indexer and SearchEngine for an INTEGRATION TEST.
        """
        indexer = InvertedIndex()
        
        # We MUST mock the total_urls now, otherwise the TF-IDF math divides by zero
        indexer.total_urls = {"http://site.com/1", "http://site.com/2", "http://site.com/3", "http://site.com/4"}
        
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

    def test_find_boolean_and_logic_with_scoring(self, setup_engine):
        """
        Proves multi-word queries return the correct URL and calculate a score.
        """
        results = setup_engine.find_pages("Good Friends") 
        
        assert len(results) == 1
        
        # Unpack the tuple: results[0] looks like ('http://site.com/2', 10.301)
        returned_url = results[0][0]
        returned_score = results[0][1]
        
        assert returned_url == "http://site.com/2"
        assert returned_score > 0.0 # Proves the math executed successfully

    def test_find_missing_word_fails_gracefully(self, setup_engine):
        results = setup_engine.find_pages("good aliens")
        assert results == []
        
    def test_find_empty_query(self, setup_engine):
        results = setup_engine.find_pages("   ")
        assert results == []
    
    def test_print_word_stats_valid_word(self, setup_engine, capsys):
        """
        Proves the print command correctly fetches and formats the index data.
        """
        setup_engine.print_word_stats("good")
        
        # Intercept the terminal output
        captured = capsys.readouterr()
        
        # Assert the correct headers and data are in the console output
        assert "Index data for 'good':" in captured.out
        assert "http://site.com/1" in captured.out
        assert "frequency" in captured.out

    def test_print_word_stats_invalid_word(self, setup_engine, capsys):
        """
        Proves the print command handles missing words gracefully without crashing.
        """
        setup_engine.print_word_stats("aliens")
        
        captured = capsys.readouterr()
        assert "The word 'aliens' was not found in the index." in captured.out

    def test_print_word_stats_empty_query(self, setup_engine, capsys):
        """
        Proves the print command handles empty or punctuation-only queries.
        """
        setup_engine.print_word_stats("   !!!   ")
        
        captured = capsys.readouterr()
        assert "Invalid search term." in captured.out