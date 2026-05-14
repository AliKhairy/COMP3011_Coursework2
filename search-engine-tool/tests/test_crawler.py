import pytest
from unittest.mock import patch, MagicMock
import requests
from src.crawler import QuoteCrawler

class TestQuoteCrawler:
    @pytest.fixture
    def crawler(self):
        """A pytest fixture to provide a fresh crawler instance for each test."""
        return QuoteCrawler(delay=6)

    @patch('src.crawler.time.sleep')
    @patch('src.crawler.requests.Session.get')
    def test_crawl_extracts_data_and_paginates(self, mock_get, mock_sleep, crawler):
        """
        Tests the 'Happy Path': successful extraction and pagination.
        We mock BOTH the network request and the time.sleep delay.
        """
        # 1. Setup the fake HTML responses
        page_1_html = """
        <html>
            <div class="quote"><span class="text">"Test quote 1"</span></div>
            <li class="next"><a href="/page/2/">Next</a></li>
        </html>
        """
        page_2_html = """
        <html>
            <div class="quote"><span class="text">"Test quote 2"</span></div>
        </html>
        """

        # 2. Configure the mock to return different responses on consecutive calls
        mock_response_1 = MagicMock()
        mock_response_1.text = page_1_html
        
        mock_response_2 = MagicMock()
        mock_response_2.text = page_2_html
        
        # side_effect allows the mock to return item 1 on the first call, item 2 on the second
        mock_get.side_effect = [mock_response_1, mock_response_2]

        # 3. Execute the function
        result = crawler.crawl()

        # 4. Assertions (The actual testing)
        assert len(result) == 2
        assert result[0]['text'] == '"Test quote 1"'
        assert result[1]['text'] == '"Test quote 2"'
        
        # Prove we tried to fetch two pages
        assert mock_get.call_count == 2
        
        # Prove we respected the politeness window without actually waiting!
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(6)

    @patch('src.crawler.time.sleep')
    @patch('src.crawler.requests.Session.get')
    def test_crawl_handles_network_exception(self, mock_get, mock_sleep, crawler):
        """
        Tests the 'Disaster Path': simulates a total network failure to ensure 
        the crawler catches the error gracefully and doesn't crash the whole app.
        """
        # Force the mock to throw a fatal network error the moment it is called
        mock_get.side_effect = requests.RequestException("Simulated Server Timeout!")

        # Execute the function. 
        # If the crawler doesn't have a try/except block, the test will crash right here.
        result = crawler.crawl()

        # Assertions
        # 1. It should safely return an empty list because it failed on the very first page
        assert result == []
        
        # 2. It should have attempted to make the request exactly once before failing
        assert mock_get.call_count == 1
        
        # 3. It STILL must respect the politeness window before making that doomed request
        assert mock_sleep.call_count == 1    