import cmd
import sys
import os

# Ensure the src directory is in the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import QuoteCrawler
from src.indexer import InvertedIndex
from src.search import SearchEngine

class SearchShell(cmd.Cmd):
    """
    Interactive command-line interface for the Search Engine.
    """
    intro = 'Welcome to the Quote Search Engine. Type help or ? to list commands.\n'
    prompt = '> ' # This perfectly matches the brief's examples

    def __init__(self):
        super().__init__()
        self.indexer = InvertedIndex()
        self.search = SearchEngine(self.indexer)

    def do_build(self, arg):
        """
        Crawls the website, builds the index, and saves it.
        Usage: build
        """
        print("Starting crawler (This will take time due to the 6-second politeness window)...")
        crawler = QuoteCrawler()
        crawled_data = crawler.crawl()
        
        if not crawled_data:
            print("Error: Crawl failed or returned no data.")
            return

        print("Building index...")
        for item in crawled_data:
            self.indexer.add_document(item['url'], item['text'])
            
        self.indexer.save_to_file()

    def do_load(self, arg):
        """
        Loads the index from the file system.
        Usage: load
        """
        self.indexer.load_from_file()

    def do_print(self, arg):
        """
        Prints the inverted index for a particular word.
        Usage: print <word>
        """
        if not arg:
            print("Please provide a word. Example: print nonsense")
            return
        self.search.print_word_stats(arg)

    def do_find(self, arg):
        """
        Finds a given query phrase and returns a list of pages containing it.
        Usage: find <word(s)>
        """
        if not arg:
            print("Please provide a query. Example: find good friends")
            return
            
        results = self.search.find_pages(arg)
        
        if results:
            print(f"\nFound {len(results)} pages matching '{arg}':")
            for i, url in enumerate(results, 1):
                print(f"{i}. {url}")
            print() # Blank line for readability
        else:
            print(f"\nNo pages found matching '{arg}'.\n")

    def do_quit(self, arg):
        """Exits the search tool."""
        print("Exiting. Goodbye!")
        return True # Returning True stops the cmd loop

    # Allow users to type 'exit' as well as 'quit'
    do_exit = do_quit

if __name__ == '__main__':
    # Start the interactive loop
    SearchShell().cmdloop()