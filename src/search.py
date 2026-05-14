import math
import json
from typing import List, Tuple
from src.indexer import InvertedIndex

class SearchEngine:
    """
    Handles querying the inverted index.
    Implements Boolean AND search, TF-IDF ranking, and Phrase Proximity scoring.
    """
    def __init__(self, indexer: InvertedIndex):
        self.indexer = indexer

    def print_word_stats(self, word: str):
        """Implements the 'print' command."""
        clean_words = self.indexer._tokenize(word)
        if not clean_words:
            print("Invalid search term.")
            return

        target_word = clean_words[0]
        
        if target_word in self.indexer.index:
            print(f"Index data for '{target_word}':")
            print(json.dumps(self.indexer.index[target_word], indent=4))
        else:
            print(f"The word '{target_word}' was not found in the index.")

    def find_pages(self, query: str) -> List[Tuple[str, float]]:
        """
        Finds pages containing ALL query words.
        Ranks them using a hybrid of TF-IDF and exact phrase proximity.
        Returns a list of tuples: (URL, Score).
        """
        query_words = self.indexer._tokenize(query)
        if not query_words:
            print("Please provide valid search words.")
            return []

        # 1. Boolean AND Filtering
        first_word = query_words[0]
        if first_word not in self.indexer.index:
            return []
            
        matching_urls = set(self.indexer.index[first_word].keys())

        for word in query_words[1:]:
            if word not in self.indexer.index:
                return [] 
            word_urls = set(self.indexer.index[word].keys())
            matching_urls = matching_urls.intersection(word_urls)

        if not matching_urls:
            return []

        # 2. Hybrid Ranking Calculation (TF-IDF + Proximity)
        total_docs = max(1, len(self.indexer.total_urls)) # Prevent division by zero
        ranked_results = []

        for url in matching_urls:
            url_score = 0.0
            
            # Step A: Base TF-IDF Score
            for word in query_words:
                tf = self.indexer.index[word][url]["frequency"]
                df = len(self.indexer.index[word])
                idf = math.log10(total_docs / df) 
                url_score += (tf * idf)

            # Step B: Phrase Proximity Bonus
            if len(query_words) > 1:
                proximity_bonus = 0.0
                # Check consecutive pairs of words in the query
                for i in range(len(query_words) - 1):
                    word1 = query_words[i]
                    word2 = query_words[i+1]
                    
                    positions1 = self.indexer.index[word1][url]["positions"]
                    positions2 = self.indexer.index[word2][url]["positions"]
                    
                    # If word2 appears exactly one position after word1, it's a phrase
                    for p1 in positions1:
                        if (p1 + 1) in positions2:
                            proximity_bonus += 10.0 # Massive algorithmic reward for exact match
                            
                url_score += proximity_bonus
                
            ranked_results.append((url, round(url_score, 4)))

        # 3. Sort by final score in descending order
        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results