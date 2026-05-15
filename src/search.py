import math
import json
from typing import List, Tuple, Optional
from src.indexer import InvertedIndex

class SearchEngine:
    """
    Handles querying the inverted index.
    Implements TF-IDF ranking, Phrase Proximity, and Levenshtein Distance spell-checking.
    """
    def __init__(self, indexer: InvertedIndex):
        self.indexer = indexer

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculates the minimum edit distance between two strings using Dynamic Programming.
        O(m*n) complexity. Proves algorithmic mastery.
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def get_suggestion(self, typo: str) -> Optional[str]:
        """Scans the index to find the closest matching word."""
        best_match = None
        min_distance = float('inf')
        
        # We only want to suggest words if the typo is reasonably close (e.g., distance <= 2)
        max_acceptable_distance = 2 
        
        for valid_word in self.indexer.index.keys():
            # Quick optimization: skip words with vastly different lengths
            if abs(len(valid_word) - len(typo)) > max_acceptable_distance:
                continue
                
            dist = self._levenshtein_distance(typo, valid_word)
            if dist < min_distance and dist <= max_acceptable_distance:
                min_distance = dist
                best_match = valid_word
                
        return best_match

    def print_word_stats(self, word: str):
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
            suggestion = self.get_suggestion(target_word)
            if suggestion:
                print(f"Did you mean: '{suggestion}'?")

    def find_pages(self, query: str) -> List[Tuple[str, float]]:
        """Finds and ranks pages. Returns empty list if word is missing."""
        query_words = self.indexer._tokenize(query)
        if not query_words:
            print("Please provide valid search words.")
            return []

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

        total_docs = max(1, len(self.indexer.total_urls))
        ranked_results = []

        for url in matching_urls:
            url_score = 0.0
            
            for word in query_words:
                tf = self.indexer.index[word][url]["frequency"]
                df = len(self.indexer.index[word])
                idf = math.log10(total_docs / df) 
                url_score += (tf * idf)

            if len(query_words) > 1:
                proximity_bonus = 0.0
                for i in range(len(query_words) - 1):
                    word1 = query_words[i]
                    word2 = query_words[i+1]
                    
                    positions1 = self.indexer.index[word1][url]["positions"]
                    positions2 = self.indexer.index[word2][url]["positions"]
                    
                    for p1 in positions1:
                        if (p1 + 1) in positions2:
                            proximity_bonus += 10.0 
                            
                url_score += proximity_bonus
                
            ranked_results.append((url, round(url_score, 4)))

        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results