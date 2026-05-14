import json
import re
from typing import Dict, List, Set

class InvertedIndex:
    """
    Manages the creation, storage, and retrieval of the inverted index.
    Stores term frequencies and positional data for advanced ranking.
    """
    def __init__(self):
        # Structure: { word: { url: {"frequency": int, "positions": [int, int]} } }
        self.index: Dict[str, Dict[str, Dict]] = {}

    def _tokenize(self, text: str) -> List[str]:
        """
        Cleans and splits text into searchable tokens.
        Handles case insensitivity, space insensitivity, and removes punctuation.
        """
        # 1. Lowercase the text to satisfy the case-insensitivity requirement
        text = text.lower()
        
        # 2. Use regex to find all alphanumeric sequences. 
        # This automatically strips out punctuation and erratic spacing/newlines.
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def add_document(self, url: str, text: str):
        """
        Tokenizes the document text and updates the index with statistics.
        """
        tokens = self._tokenize(text)
        
        for position, word in enumerate(tokens):
            if word not in self.index:
                self.index[word] = {}
                
            if url not in self.index[word]:
                self.index[word][url] = {"frequency": 0, "positions": []}
                
            self.index[word][url]["frequency"] += 1
            self.index[word][url]["positions"].append(position)

    def save_to_file(self, filepath: str = "data/index.json"):
        """Saves the index to the file system."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=4)
        print(f"Index successfully saved to {filepath}")

    def load_from_file(self, filepath: str = "data/index.json"):
        """Loads the index from the file system."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
            print(f"Index successfully loaded from {filepath}")
        except FileNotFoundError:
            print(f"Error: Could not find index file at {filepath}. Run 'build' first.")