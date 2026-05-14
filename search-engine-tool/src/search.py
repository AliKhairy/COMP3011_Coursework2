from typing import List
from src.indexer import InvertedIndex

class SearchEngine:
    """
    Handles querying the inverted index.
    Currently implements Boolean AND search for multi-word queries.
    """
    def __init__(self, indexer: InvertedIndex):
        # The search engine needs access to the loaded index
        self.indexer = indexer

    def print_word_stats(self, word: str):
        """Implements the 'print' command."""
        # Clean the search word just like we cleaned the text
        clean_words = self.indexer._tokenize(word)
        if not clean_words:
            print("Invalid search term.")
            return

        target_word = clean_words[0]
        
        if target_word in self.indexer.index:
            print(f"Index data for '{target_word}':")
            # Pretty print the dictionary for that specific word
            import json
            print(json.dumps(self.indexer.index[target_word], indent=4))
        else:
            print(f"The word '{target_word}' was not found in the index.")

    def find_pages(self, query: str) -> List[str]:
        """
        Implements the 'find' command. 
        Returns URLs containing ALL words in the query (Boolean AND).
        """
        query_words = self.indexer._tokenize(query)
        
        if not query_words:
            print("Please provide valid search words.")
            return []

        # Start with the set of URLs for the first word
        first_word = query_words[0]
        if first_word not in self.indexer.index:
            return [] # If the first word isn't there, the AND condition fails immediately
            
        # Get the initial set of URLs
        matching_urls = set(self.indexer.index[first_word].keys())

        # Intersect with the URL sets of all subsequent words
        for word in query_words[1:]:
            if word not in self.indexer.index:
                return [] # If any word is missing, return empty list
            
            word_urls = set(self.indexer.index[word].keys())
            # Keep only URLs that are in both the current matching_urls AND the new word_urls
            matching_urls = matching_urls.intersection(word_urls)

        return list(matching_urls)