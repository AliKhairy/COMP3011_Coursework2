def test_save_and_load_file_io(self, indexer, tmp_path):
        """
        Proves the indexer can serialize its data to JSON and save it to the OS.
        Uses pytest's tmp_path fixture to avoid creating real files.
        """
        # 1. Setup: Add some dummy data to the index
        indexer.add_document("http://io-test.com", "save me")
        
        # 2. Create a temporary, isolated file path
        test_file = tmp_path / "test_data" / "test_index.json"
        
        # 3. Execute the save
        indexer.save_to_file(str(test_file))
        
        # 4. Assert the file actually generated on the (temporary) hard drive
        assert test_file.exists()
        
        # 5. Create a completely blank, secondary indexer
        new_indexer = InvertedIndex()
        
        # 6. Load the temporary file into the new indexer
        new_indexer.load_from_file(str(test_file))
        
        # 7. Assert the data survived the round trip!
        assert "save" in new_indexer.index
        assert "me" in new_indexer.index
        assert len(new_indexer.total_urls) == 1

    def test_load_file_not_found_graceful_fail(self, indexer, capsys):
        """
        Proves the system doesn't crash if the user types 'load' before 'build'.
        """
        # Attempt to load a file that mathematically cannot exist
        indexer.load_from_file("path/to/absolute/nowhere.json")
        
        # Capture the terminal output to prove it printed an error instead of crashing
        captured = capsys.readouterr()
        assert "Error: Could not find index file" in captured.out