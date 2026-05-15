import time
import random
import tracemalloc
from src.indexer import InvertedIndex
from src.search import SearchEngine

def generate_dummy_data(size: int, vocab_size: int = 5000) -> InvertedIndex:
    """Generates an index with a large vocabulary to simulate real-world data distribution."""
    indexer = InvertedIndex()
    
    # Create a massive simulated vocabulary (e.g., word_0, word_1, ... word_5000)
    vocabulary = [f"word_{i}" for i in range(vocab_size)]
    
    for i in range(size):
        doc_length = random.randint(20, 50)
        text = " ".join(random.choices(vocabulary, k=doc_length))
        
        # Inject target phrases
        if i % 10 == 0:
            text += " good friends quote"
            
        indexer.add_document(f"http://benchmark.test/{i}", text)
        
    return indexer

def run_advanced_benchmark():
    print("==================================================================================")
    print(" ADVANCED SEARCH ENGINE PERFORMANCE BENCHMARK (TIME & MEMORY)")
    print("==================================================================================")
    
    document_sizes = [1000, 10000, 50000]
    
    # Define distinct query profiles to test different algorithmic pathways
    queries = {
        "Single Word": "quote",
        "Multi-Word (AND)": "good friends",
        "Typo (Levenshtein)": "qoote" # Forces the engine to scan the keys for suggestions
    }
    
    print(f"{'Docs Indexed':<15} | {'Peak RAM (MB)':<15} | {'Build Time':<12} | {'Query Type':<20} | {'Avg Search (ms)':<15}")
    print("-" * 85)
    
    for size in document_sizes:
        # Start Memory Tracker
        tracemalloc.start()
        
        start_build = time.time()
        indexer = generate_dummy_data(size)
        build_time = time.time() - start_build
        
        # Capture peak memory usage during the build phase
        _, peak_memory = tracemalloc.get_traced_memory()
        peak_memory_mb = peak_memory / (1024 * 1024)
        tracemalloc.stop()
        
        search_engine = SearchEngine(indexer)
        iterations = 100
        
        # Benchmark each query type against the current index size
        for query_name, query_text in queries.items():
            start_search = time.time()
            
            for _ in range(iterations):
                search_engine.find_pages(query_text)
                
            avg_search_time_ms = ((time.time() - start_search) / iterations) * 1000
            
            # Print the row (only print Build Time and RAM on the first query for cleanliness)
            if query_name == "Single Word":
                print(f"{size:<15} | {peak_memory_mb:<15.2f} | {build_time:<11.4f}s | {query_name:<20} | {avg_search_time_ms:<15.4f}")
            else:
                print(f"{'':<15} | {'':<15} | {'':<12} | {query_name:<20} | {avg_search_time_ms:<15.4f}")
        print("-" * 85)

if __name__ == "__main__":
    run_advanced_benchmark()