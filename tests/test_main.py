import pytest
from unittest.mock import patch, MagicMock
from src.main import SearchShell

class TestSearchShell:
    @pytest.fixture
    def shell(self):
        """Provides a fresh interactive shell for each test."""
        return SearchShell()

    @patch('src.main.QuoteCrawler.crawl')
    def test_do_build_success(self, mock_crawl, shell, capsys):
        """
        Proves the build command correctly orchestrates the Crawler and Indexer.
        We mock the crawler so the test runs instantly without hitting the real web.
        """
        # Inject fake crawled data to instantly bypass the network delay
        mock_crawl.return_value = [{"url": "http://test.com", "text": "hello world"}]
        
        # Simulate the user typing 'build'
        shell.do_build("")
        
        captured = capsys.readouterr()
        
        # Verify the orchestrator triggered the right prints and logic
        assert "Starting crawler" in captured.out
        assert "Index successfully saved" in captured.out
        assert mock_crawl.call_count == 1

    def test_do_find_empty_query(self, shell, capsys):
        """Proves the CLI handles empty find commands gracefully."""
        # Simulate the user typing 'find' and hitting Enter without a word
        shell.do_find("")
        
        captured = capsys.readouterr()
        assert "Please provide a query." in captured.out

    def test_do_quit(self, shell, capsys):
        """Proves the quit command correctly signals the cmd loop to terminate."""
        # Simulate the user typing 'quit'
        result = shell.do_quit("")
        
        captured = capsys.readouterr()
        assert "Exiting." in captured.out
        # In the cmd module, returning True is what breaks the infinite loop
        assert result is True