"""
Unit tests for the VectorMemory class.

Run with:
    pytest tests/test_vector_memory.py -v
    pytest tests/test_vector_memory.py -v --cov=memory.vector_store
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.vector_store import VectorMemory


@pytest.fixture
def temp_db_dir():
    """Create temporary directory for test database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir)


@pytest.fixture
def memory(temp_db_dir):
    """Create VectorMemory instance with temporary database."""
    return VectorMemory(persist_dir=temp_db_dir)


class TestVectorMemoryInitialization:
    """Test initialization and basic properties."""
    
    def test_initialization(self, memory):
        """Test that VectorMemory initializes correctly."""
        stats = memory.get_stats()
        assert stats['total_exchanges'] == 0
        assert stats['collection_name'] == 'conversations'
        assert stats['embedding_dimension'] == 384
    
    def test_custom_collection_name(self, temp_db_dir):
        """Test initialization with custom collection name."""
        custom_memory = VectorMemory(
            collection_name="test_collection",
            persist_dir=temp_db_dir
        )
        stats = custom_memory.get_stats()
        assert stats['collection_name'] == 'test_collection'


class TestAddExchange:
    """Test adding conversation exchanges."""
    
    def test_add_single_exchange(self, memory):
        """Test adding a single exchange."""
        exchange_id = memory.add_exchange(
            "What is Python?",
            "Python is a programming language."
        )
        
        assert isinstance(exchange_id, str)
        assert len(exchange_id) > 0
        assert memory.get_stats()['total_exchanges'] == 1
    
    def test_add_multiple_exchanges(self, memory):
        """Test adding multiple exchanges."""
        exchanges = [
            ("What is Python?", "Python is a programming language."),
            ("What is Java?", "Java is another programming language."),
            ("What is JavaScript?", "JavaScript is used for web development.")
        ]
        
        for user_msg, bot_resp in exchanges:
            memory.add_exchange(user_msg, bot_resp)
        
        assert memory.get_stats()['total_exchanges'] == 3
    
    def test_add_with_metadata(self, memory):
        """Test adding exchange with custom metadata."""
        exchange_id = memory.add_exchange(
            "Test question",
            "Test answer",
            metadata={"topic": "testing", "rating": 5}
        )
        
        assert exchange_id is not None
        stats = memory.get_stats()
        assert stats['total_exchanges'] == 1


class TestSearch:
    """Test semantic search functionality."""
    
    def test_search_similar_empty_db(self, memory):
        """Test search on empty database."""
        results = memory.search_similar("test query")
        assert results == []
    
    def test_search_similar_basic(self, memory):
        """Test basic semantic search."""
        # Add programming-related exchanges
        memory.add_exchange(
            "What is Python?",
            "Python is a high-level programming language known for simplicity."
        )
        memory.add_exchange(
            "How to learn machine learning?",
            "Start with Python basics, then NumPy, Pandas, and scikit-learn."
        )
        memory.add_exchange(
            "Best pizza toppings?",
            "Pepperoni and mushrooms are classic choices."
        )
        
        # Search for programming question
        results = memory.search_similar("Tell me about Python programming", n_results=2)
        
        assert len(results) == 2
        # First result should be about Python
        assert "Python" in results[0]['user_message']
        # Should have similarity scores
        assert 0 <= results[0]['similarity'] <= 1
        assert results[0]['similarity'] > results[1]['similarity']
    
    def test_search_with_min_similarity(self, memory):
        """Test search with minimum similarity threshold."""
        memory.add_exchange("What is AI?", "AI is artificial intelligence.")
        memory.add_exchange("Best pizza?", "Margherita is great.")
        
        # Search with high threshold - pizza shouldn't match AI query
        results = memory.search_similar(
            "Tell me about artificial intelligence",
            n_results=2,
            min_similarity=0.5
        )
        
        # Should only return AI-related result
        assert len(results) >= 1
        assert "AI" in results[0]['user_message'] or "intelligence" in results[0]['bot_response']
    
    def test_search_n_results_limit(self, memory):
        """Test that n_results parameter limits results."""
        # Add 5 exchanges
        for i in range(5):
            memory.add_exchange(f"Question {i}", f"Answer {i}")
        
        # Request only 3 results
        results = memory.search_similar("Question", n_results=3)
        assert len(results) == 3


class TestGetRelevantContext:
    """Test formatted context retrieval."""
    
    def test_get_relevant_context_empty(self, memory):
        """Test getting context from empty database."""
        context = memory.get_relevant_context("test query")
        assert "No relevant" in context
    
    def test_get_relevant_context_format(self, memory):
        """Test context formatting."""
        memory.add_exchange("What is AI?", "AI is artificial intelligence.")
        memory.add_exchange("What is ML?", "ML is machine learning.")
        
        context = memory.get_relevant_context("artificial intelligence", n_results=2)
        
        # Check format markers
        assert "RELEVANT PAST CONVERSATIONS" in context
        assert "[1]" in context
        assert "User:" in context
        assert "Assistant:" in context
        assert "similarity:" in context.lower()


class TestPersistence:
    """Test database persistence across instances."""
    
    def test_persistence(self, temp_db_dir):
        """Test that data persists across VectorMemory instances."""
        # Create first instance and add data
        memory1 = VectorMemory(persist_dir=temp_db_dir)
        memory1.add_exchange("Test question", "Test answer")
        assert memory1.get_stats()['total_exchanges'] == 1
        
        # Delete first instance
        del memory1
        
        # Create new instance with same directory
        memory2 = VectorMemory(persist_dir=temp_db_dir)
        
        # Should still have the data
        assert memory2.get_stats()['total_exchanges'] == 1
        
        # Should be able to search for it
        results = memory2.search_similar("Test question")
        assert len(results) == 1
        assert results[0]['user_message'] == "Test question"


class TestClearAndExport:
    """Test clearing and exporting functionality."""
    
    def test_clear_all(self, memory):
        """Test clearing all exchanges."""
        # Add some data
        memory.add_exchange("Q1", "A1")
        memory.add_exchange("Q2", "A2")
        assert memory.get_stats()['total_exchanges'] == 2
        
        # Clear
        memory.clear_all()
        
        # Should be empty
        assert memory.get_stats()['total_exchanges'] == 0
    
    def test_export_all_empty(self, memory):
        """Test exporting from empty database."""
        exchanges = memory.export_all()
        assert exchanges == []
    
    def test_export_all(self, memory):
        """Test exporting all exchanges."""
        # Add data
        test_exchanges = [
            ("Q1", "A1"),
            ("Q2", "A2"),
            ("Q3", "A3")
        ]
        
        for user_msg, bot_resp in test_exchanges:
            memory.add_exchange(user_msg, bot_resp)
        
        # Export
        exported = memory.export_all()
        
        assert len(exported) == 3
        
        # Check structure
        for ex in exported:
            assert 'user_message' in ex
            assert 'bot_response' in ex
            assert 'timestamp' in ex
            assert 'metadata' in ex


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_message(self, memory):
        """Test adding exchange with empty strings."""
        exchange_id = memory.add_exchange("", "")
        assert exchange_id is not None
        assert memory.get_stats()['total_exchanges'] == 1
    
    def test_very_long_message(self, memory):
        """Test adding exchange with very long text."""
        long_text = "A" * 10000  # 10k characters
        exchange_id = memory.add_exchange(long_text, "Short answer")
        
        assert exchange_id is not None
        results = memory.search_similar(long_text[:100])
        assert len(results) == 1
    
    def test_special_characters(self, memory):
        """Test handling special characters."""
        special_msg = "Test with émojis 🎉 and spëcial çhars!"
        memory.add_exchange(special_msg, "Response")
        
        results = memory.search_similar(special_msg)
        assert len(results) == 1
        assert special_msg in results[0]['user_message']


class TestSearchByDateRange:
    """Test date-based filtering."""
    
    def test_search_by_date_range(self, memory):
        """Test searching within a date range."""
        # Add exchanges (they'll have today's timestamp)
        memory.add_exchange("Q1", "A1")
        memory.add_exchange("Q2", "A2")
        
        # Get today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Search with date range including today
        results = memory.search_by_date_range(today, today, n_results=10)
        
        assert len(results) == 2
    
    def test_search_by_date_range_empty(self, memory):
        """Test date range search with no matches."""
        memory.add_exchange("Q1", "A1")
        
        # Search in future date range
        results = memory.search_by_date_range("2030-01-01", "2030-12-31")
        
        assert len(results) == 0


# Integration test
class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_realistic_conversation_flow(self, memory):
        """Test a realistic multi-turn conversation."""
        # Conversation about programming
        conversations = [
            ("What is Python?", "Python is a versatile programming language."),
            ("How do I install Python?", "Download from python.org and run installer."),
            ("What's a good IDE?", "PyCharm and VS Code are popular choices."),
            ("How to learn Python?", "Start with basics, then build projects."),
            # Different topic
            ("What's for dinner?", "How about pasta?")
        ]
        
        # Add all conversations
        for user, bot in conversations:
            memory.add_exchange(user, bot)
        
        # New query about Python
        context = memory.get_relevant_context("Python programming tips", n_results=3)
        
        # Should retrieve Python-related conversations
        assert "Python" in context
        # Should not retrieve dinner conversation
        assert "dinner" not in context.lower() or "pasta" not in context.lower()
        
        # Stats check
        stats = memory.get_stats()
        assert stats['total_exchanges'] == 5


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
