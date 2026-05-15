import pytest
from unittest.mock import patch, MagicMock
from src.crawler import QuoteCrawler

class TestQuoteCrawler:
    @pytest.fixture
    def crawler(self):
        """Provides a fresh crawler. Manually bypasses delay for fast tests."""
        c = QuoteCrawler()
        c.delay = 0 # Forces the test to run instantly instead of waiting 6 seconds
        return c

    @patch('src.crawler.requests.get')
    def test_spider_trap_prevention(self, mock_get, crawler):
        """Proves the crawler stops if a website loops back to a visited URL."""
        mock_response = MagicMock()
        # The fake page links back to itself ("/")
        mock_response.text = '<html><div class="quote"><span class="text">Loop</span></div><li class="next"><a href="/">Next</a></li></html>'
        mock_get.return_value = mock_response

        crawler.base_url = "http://loop.com/"
        quotes = crawler.crawl()
        
        # It should scrape once, hit the guard, and break the loop instantly
        assert len(quotes) == 1
        assert len(crawler.visited) == 1

    @patch('src.crawler.requests.get')
    def test_malformed_html_skipped(self, mock_get, crawler):
        """Proves the crawler skips broken quotes instead of crashing."""
        mock_response = MagicMock()
        mock_response.text = '<html><div class="quote">Missing the span tag entirely!</div></html>'
        mock_get.return_value = mock_response
        
        crawler.base_url = "http://broken.com"
        quotes = crawler.crawl()
        
        # Should gracefully skip the bad data and return nothing
        assert len(quotes) == 0

    @patch('src.crawler.requests.get')
    def test_crawl_handles_network_exception(self, mock_get, crawler):
        """Proves the crawler handles dead links gracefully."""
        import requests
        mock_get.side_effect = requests.RequestException("Simulated Network Error")
        
        quotes = crawler.crawl()
        assert quotes == []