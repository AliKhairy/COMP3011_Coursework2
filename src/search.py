import math
import json
from typing import List, Tuple, Optional, Dict
from src.indexer import InvertedIndex

class SearchEngine:
    """
    Handles advanced querying.
    Implements TF-IDF, Phrase Proximity, Levenshtein Distance, and Custom Stemming.
    """
    def __init__(self, indexer: InvertedIndex):
        self.indexer = indexer

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculates minimum edit distance for spell-checking."""
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

    def _stem(self, word: str) -> str:
        """
        A custom algorithm to strip common English suffixes.
        Handles double-consonant grammar edge cases.
        """
        if len(word) <= 3:
            return word
            
        stem = word
        if word.endswith('ing'):
            stem = word[:-3]
        elif word.endswith('ed'):
            stem = word[:-2]
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1] # Return early for plurals
            
        # The Double Consonant Fix (e.g., runn -> run, mapp -> map)
        # We ignore 'l', 's', and 'z' because words like 'roll' or 'boss' are naturally double
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
            stem = stem[:-1]
            
        return stem

    def get_suggestion(self, typo: str) -> Optional[str]:
        """Scans the index to find the closest matching word."""
        best_match = None
        min_distance = float('inf')
        max_acceptable_distance = 2 
        
        for valid_word in self.indexer.index.keys():
            if abs(len(valid_word) - len(typo)) > max_acceptable_distance:
                continue
            dist = self._levenshtein_distance(typo, valid_word)
            if dist < min_distance and dist <= max_acceptable_distance:
                min_distance = dist
                best_match = valid_word
                
        return best_match

    def print_word_stats(self, word: str):
        """Prints exact index data or offers spelling suggestions."""
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
        """Finds pages using Stem Expansion and applies multi-layered ranking."""
        query_words = self.indexer._tokenize(query)
        if not query_words:
            print("Please provide valid search words.")
            return []

        # 1. Stem Expansion Mapping
        # We map the exact word to ALL variants in the index that share the same stem
        expanded_query: List[Dict] = []
        for q_word in query_words:
            q_stem = self._stem(q_word)
            matched_keys = [k for k in self.indexer.index.keys() if self._stem(k) == q_stem]
            expanded_query.append({
                "exact": q_word,
                "keys": matched_keys
            })

        # 2. Boolean AND Filtering (using expanded word pools)
        if any(not eq["keys"] for eq in expanded_query):
            return [] # One of the words (and all its variants) is completely missing

        matching_urls = set()
        for k in expanded_query[0]["keys"]:
            matching_urls.update(self.indexer.index[k].keys())

        for eq in expanded_query[1:]:
            word_urls = set()
            for k in eq["keys"]:
                word_urls.update(self.indexer.index[k].keys())
            matching_urls = matching_urls.intersection(word_urls)

        if not matching_urls:
            return []

        # 3. Hybrid Ranking (TF-IDF + Exact Match Bonus + Proximity Bonus)
        total_docs = max(1, len(self.indexer.total_urls))
        ranked_results = []

        for url in matching_urls:
            url_score = 0.0
            
            # A: TF-IDF and Exact Match Bonus
            for eq in expanded_query:
                exact_word = eq["exact"]
                
                for k in eq["keys"]:
                    if url in self.indexer.index[k]:
                        tf = self.indexer.index[k][url]["frequency"]
                        df = len(self.indexer.index[k])
                        idf = math.log10(total_docs / df)
                        base_score = tf * idf
                        
                        # THE USER'S EXACT MATCH SCORE BONUS
                        if k == exact_word:
                            base_score += 5.0 
                            
                        url_score += base_score

            # B: Exact Phrase Proximity Bonus
            if len(query_words) > 1:
                proximity_bonus = 0.0
                for i in range(len(query_words) - 1):
                    word1 = query_words[i]
                    word2 = query_words[i+1]
                    
                    # We only reward proximity if the EXACT literal words are next to each other
                    if word1 in self.indexer.index and word2 in self.indexer.index:
                        if url in self.indexer.index[word1] and url in self.indexer.index[word2]:
                            positions1 = self.indexer.index[word1][url]["positions"]
                            positions2 = self.indexer.index[word2][url]["positions"]
                            for p1 in positions1:
                                if (p1 + 1) in positions2:
                                    proximity_bonus += 10.0 
                                    
                url_score += proximity_bonus
                
            ranked_results.append((url, round(url_score, 4)))

        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results