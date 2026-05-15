import json
import re
import os
from typing import Dict, List, Set

class InvertedIndex:
    """
    Manages the creation, storage, and retrieval of the inverted index.
    Optimized for memory usage and idempotent data entry.
    """
    
    # Class-level constant: Loads into RAM exactly once.
    STOP_WORDS: Set[str] = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", 
        "and", "any", "are", "aren't", "as", "at", "be", "because", "been", 
        "before", "being", "below", "between", "both", "but", "by", "can't", 
        "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
        "doing", "don't", "down", "during", "each", "few", "for", "from", 
        "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", 
        "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", 
        "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
        "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
        "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", 
        "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", 
        "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", 
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
        "then", "there", "there's", "these", "they", "they'd", "they'll", 
        "they're", "they've", "this", "those", "through", "to", "too", "under", 
        "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
        "we've", "were", "weren't", "what", "what's", "when", "when's", "where", 
        "where's", "which", "while", "who", "who's", "whom", "why", "why's", 
        "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", 
        "you've", "your", "yours", "yourself", "yourselves"
    }

    def __init__(self):
        self.index: Dict[str, Dict[str, Dict]] = {}
        self.total_urls: Set[str] = set() 

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        # Reference the class-level STOP_WORDS
        return [token for token in tokens if token not in self.STOP_WORDS]

    def add_document(self, url: str, text: str):
        # IDEMPOTENCY GUARD: If URL is already in the set, abort to prevent duplication
        if url in self.total_urls:
            return 
            
        self.total_urls.add(url)
        tokens = self._tokenize(text)
        
        for position, word in enumerate(tokens):
            if word not in self.index:
                self.index[word] = {}
            if url not in self.index[word]:
                self.index[word][url] = {"frequency": 0, "positions": []}
                
            self.index[word][url]["frequency"] += 1
            self.index[word][url]["positions"].append(position)

    def save_to_file(self, filepath: str = "data/index.json"):
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        data_to_save = {
            "total_document_count": len(self.total_urls),
            "index": self.index
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Index successfully saved to {filepath}")

    def load_from_file(self, filepath: str = "data/index.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.index = data["index"]
                self.total_urls = set(range(data.get("total_document_count", 0))) 
            print(f"Index successfully loaded from {filepath}")
        except FileNotFoundError:
            print(f"Error: Could not find index file at {filepath}. Run 'build' first.")