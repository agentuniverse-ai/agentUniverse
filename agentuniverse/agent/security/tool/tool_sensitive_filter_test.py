import pytest
from unittest.mock import mock_open, patch, MagicMock

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.security.tool.tool_sensitive_filter import SensitiveWordFilter


@pytest.fixture
def filter_instance():
    with patch('builtins.open', mock_open(read_data="bad\nworse\nworst\n")):
        return SensitiveWordFilter()

@pytest.fixture
def empty_filter():
    with patch('builtins.open', mock_open(read_data="")):
        return SensitiveWordFilter()

class TestSensitiveWordFilter:
    def test_initialization(self, filter_instance):
        """Test proper initialization of SensitiveWordFilter"""
        assert filter_instance.tool_type == ToolTypeEnum.FUNC
        assert filter_instance.name == "sensitive_word_filter"
        assert filter_instance.input_keys == ["text"]
        assert isinstance(filter_instance.word_list, list)
        assert isinstance(filter_instance.trie, dict)

    def test_load_words(self, filter_instance):
        """Test loading words from file"""
        assert filter_instance.word_list == ["bad", "worse", "worst"]

        # Test loading empty file
        with patch('builtins.open', mock_open(read_data="")):
            words = filter_instance.load_words("dummy/path")
            assert words == []

    def test_build_trie(self, filter_instance):
        """Test Trie construction"""
        words = ["cat", "cats"]
        trie = filter_instance.build_trie(words)

        # Verify trie structure
        assert 'c' in trie
        assert 'a' in trie['c']
        assert 't' in trie['c']['a']
        assert '#' in trie['c']['a']['t']  # End marker for "cat"
        assert 's' in trie['c']['a']['t']  # Continuation for "cats"
        assert '#' in trie['c']['a']['t']['s']  # End marker for "cats"

    def test_filter_text_basic(self, filter_instance):
        """Test basic text filtering"""
        # Simple word replacement
        assert filter_instance.filter_text("bad") == "***"
        assert filter_instance.filter_text("worse") == "*****"
        assert filter_instance.filter_text("worst") == "*****"

    def test_filter_text_complex(self, filter_instance):
        """Test complex text filtering scenarios"""
        # Words within text
        assert filter_instance.filter_text("This is bad behavior") == "This is *** behavior"
        # Multiple sensitive words
        assert filter_instance.filter_text("bad and worse things") == "*** and ***** things"
        # Overlapping words
        text = "worst case is bad"
        assert filter_instance.filter_text(text) == "***** case is ***"
        # Custom replacement character
        assert filter_instance.filter_text("bad", replace_char="#") == "###"

    def test_filter_text_edge_cases(self, empty_filter):
        """Test edge cases for text filtering"""
        # Empty text
        assert empty_filter.filter_text("") == ""
        # Text with no sensitive words
        assert empty_filter.filter_text("hello world") == "hello world"
        # Single character
        assert empty_filter.filter_text("a") == "a"
        # Special characters
        assert empty_filter.filter_text("hello!@#$%^&*()") == "hello!@#$%^&*()"

    def test_execute(self, filter_instance):
        """Test execute method with ToolInput"""
        # Valid input
        tool_input = ToolInput({"text": "This is bad"})
        assert filter_instance.execute(tool_input) == "This is ***"

        # Invalid input
        with pytest.raises(ValueError):
            filter_instance.execute(ToolInput({"invalid_key": "value"}))

    def test_concurrent_access(self, filter_instance):
        """Test concurrent access to filter"""
        import threading
        import queue

        results = queue.Queue()

        def filter_text():
            result = filter_instance.filter_text("bad and worse")
            results.put(result)

        # Create multiple threads
        threads = [threading.Thread(target=filter_text) for _ in range(5)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all results are consistent
        expected = "*** and *****"
        while not results.empty():
            assert results.get() == expected

if __name__ == '__main__':
    pytest.main([__file__])