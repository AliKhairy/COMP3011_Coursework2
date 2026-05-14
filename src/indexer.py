import json
import re
import os
from typing import Dict, List, Set

class InvertedIndex:
    """
    Manages the creation, storage, and retrieval of the inverted index.
    Stores term frequencies and positional data for advanced ranking.
    """
    def __init__(self):
        # Structure: { word: { url: {"frequency": int, "positions": [int, int]} } }
        self.index: Dict[str, Dict[str, Dict]] = {}
        # Track unique URLs to calculate total documents for TF-IDF math
        self.total_urls: Set[str] = set() 

    def _tokenize(self, text: str) -> List[str]:
        """Cleans and splits text into searchable tokens."""
        text = text.lower()
        return re.findall(r'\b\w+\b', text)

    def add_document(self, url: str, text: str):
        """Tokenizes text and updates the index with statistics."""
        self.total_urls.add(url) # Track the document for IDF calculations
        tokens = self._tokenize(text)
        
        for position, word in enumerate(tokens):
            if word not in self.index:
                self.index[word] = {}
                
            if url not in self.index[word]:
                self.index[word][url] = {"frequency": 0, "positions": []}
                
            self.index[word][url]["frequency"] += 1
            self.index[word][url]["positions"].append(position)

    def save_to_file(self, filepath: str = "data/index.json"):
        """Saves the index to the file system, creating directories if needed."""
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # Package the total_urls count alongside the index data
        data_to_save = {
            "total_document_count": len(self.total_urls),
            "index": self.index
        }
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Index successfully saved to {filepath}")

    def load_from_file(self, filepath: str = "data/index.json"):
        """Loads the index from the file system."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.index = data["index"]
                # Reconstruct a dummy set to maintain the correct length for math operations
                self.total_urls = set(range(data.get("total_document_count", 0))) 
            print(f"Index successfully loaded from {filepath}")
        except FileNotFoundError:
            print(f"Error: Could not find index file at {filepath}. Run 'build' first.")