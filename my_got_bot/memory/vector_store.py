"""
Vector-based long-term memory using ChromaDB.
Stores conversation exchanges as embeddings for semantic search.

This module provides persistent, semantic search capabilities over
all historical conversations using vector embeddings.

Requirements:
    pip install chromadb sentence-transformers
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class VectorMemory:
    """
    Long-term memory with semantic search capabilities.
    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    
    Features:
    - Persistent storage (survives restarts)
    - Semantic search (finds similar past conversations)
    - Efficient retrieval (optimized for speed)
    - Automatic embedding generation
    """
    
    def __init__(
        self, 
        collection_name: str = "conversations", 
        persist_dir: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB client and embedding model.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_dir: Directory to persist database
            embedding_model: Sentence-transformers model name
                            (all-MiniLM-L6-v2: 384-dim, fast, good quality)
        """
        # Initialize ChromaDB client with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Chat conversation history with semantic search"}
        )
        
        # Initialize embedding model
        # all-MiniLM-L6-v2: 384 dimensions, 14M params, ~120MB
        # Fast inference, good for semantic similarity
        self.encoder = SentenceTransformer(embedding_model)
        
        print(f"🧠 VectorMemory initialized")
        print(f"   Collection: {collection_name}")
        print(f"   Stored exchanges: {self.collection.count()}")
        print(f"   Embedding model: {embedding_model}")
    
    def add_exchange(
        self, 
        user_message: str, 
        bot_response: str, 
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a conversation exchange to vector memory.
        
        Args:
            user_message: User's input
            bot_response: Bot's response
            metadata: Optional metadata (tags, ratings, etc.)
        
        Returns:
            Exchange ID (UUID)
        
        Example:
            exchange_id = memory.add_exchange(
                "What is Python?",
                "Python is a high-level programming language.",
                metadata={"topic": "programming", "rating": 5}
            )
        """
        # Create combined text for embedding
        # Format: "User: <msg>\nAssistant: <response>"
        combined_text = f"User: {user_message}\nAssistant: {bot_response}"
        
        # Generate embedding vector (384 dimensions)
        embedding = self.encoder.encode(combined_text).tolist()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "user_length": len(user_message),
            "bot_length": len(bot_response)
        })
        
        # Generate unique ID
        exchange_id = str(uuid.uuid4())
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[metadata],
            ids=[exchange_id]
        )
        
        return exchange_id
    
    def search_similar(
        self, 
        query: str, 
        n_results: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Search for semantically similar past exchanges.
        
        Args:
            query: Search query (user message or question)
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of dicts with:
            - user_message: Original user input
            - bot_response: Bot's response
            - similarity: Similarity score (0-1, higher is better)
            - timestamp: When exchange occurred
        
        Example:
            results = memory.search_similar("Python programming", n_results=3)
            for r in results:
                print(f"[{r['similarity']:.2f}] {r['user_message']}")
        """
        if self.collection.count() == 0:
            return []
        
        # Encode query
        query_embedding = self.encoder.encode(query).tolist()
        
        # Search ChromaDB (cosine similarity)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count())
        )
        
        # Format results
        formatted_results = []
        if results['metadatas'] and results['distances']:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                # Convert L2 distance to similarity score (0-1)
                # Lower distance = higher similarity
                similarity = 1 / (1 + distance)
                
                if similarity >= min_similarity:
                    formatted_results.append({
                        'user_message': metadata.get('user_message', ''),
                        'bot_response': metadata.get('bot_response', ''),
                        'similarity': similarity,
                        'timestamp': metadata.get('timestamp', ''),
                        'metadata': metadata
                    })
        
        return formatted_results
    
    def get_relevant_context(
        self, 
        current_message: str, 
        n_results: int = 3,
        min_similarity: float = 0.3
    ) -> str:
        """
        Get formatted relevant context from past conversations.
        
        This is the main function to use in your prompt pipeline.
        It retrieves similar past exchanges and formats them nicely
        for inclusion in the LLM prompt.
        
        Args:
            current_message: Current user message
            n_results: Number of past exchanges to retrieve
            min_similarity: Minimum similarity threshold
        
        Returns:
            Formatted string of relevant past exchanges
        
        Example:
            context = memory.get_relevant_context("What is AI?", n_results=2)
            # Returns:
            # "Relevant past conversations:
            #  [1] User: What is machine learning?
            #      Assistant: Machine learning is...
            #      (similarity: 0.85)"
        """
        similar = self.search_similar(
            current_message, 
            n_results=n_results,
            min_similarity=min_similarity
        )
        
        if not similar:
            return "No relevant past conversations found."
        
        context_parts = ["=== RELEVANT PAST CONVERSATIONS ==="]
        for i, ex in enumerate(similar, 1):
            # Format each exchange with similarity score
            context_parts.append(
                f"\n[{i}] Similarity: {ex['similarity']:.2f} | {ex['timestamp'][:10]}\n"
                f"    User: {ex['user_message']}\n"
                f"    Assistant: {ex['bot_response'][:200]}{'...' if len(ex['bot_response']) > 200 else ''}"
            )
        
        context_parts.append("\n" + "="*50)
        return "\n".join(context_parts)
    
    def clear_all(self):
        """
        Clear all stored exchanges.
        
        Warning: This is destructive and cannot be undone!
        """
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            self.collection.name,
            metadata={"description": "Chat conversation history with semantic search"}
        )
        print("🗑️  All exchanges cleared from vector memory")
    
    def get_stats(self) -> Dict:
        """
        Get memory statistics.
        
        Returns:
            Dict with total_exchanges, collection_name, embedding_dim
        """
        return {
            "total_exchanges": self.collection.count(),
            "collection_name": self.collection.name,
            "embedding_dimension": 384,  # all-MiniLM-L6-v2
            "model": "all-MiniLM-L6-v2"
        }
    
    def export_all(self) -> List[Dict]:
        """
        Export all stored exchanges.
        
        Useful for:
        - Backing up conversations
        - Analyzing conversation patterns
        - Migrating to another system
        
        Returns:
            List of all exchanges with metadata
        """
        if self.collection.count() == 0:
            return []
        
        # Get all documents
        results = self.collection.get()
        
        exchanges = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                exchanges.append({
                    'user_message': metadata.get('user_message'),
                    'bot_response': metadata.get('bot_response'),
                    'timestamp': metadata.get('timestamp'),
                    'metadata': metadata
                })
        
        return exchanges
    
    def search_by_date_range(
        self, 
        start_date: str, 
        end_date: str,
        n_results: int = 100
    ) -> List[Dict]:
        """
        Search exchanges within a date range.
        
        Args:
            start_date: ISO format date string (e.g., "2024-01-01")
            end_date: ISO format date string
            n_results: Max results to return
        
        Returns:
            List of exchanges within date range
        """
        all_exchanges = self.export_all()
        
        filtered = [
            ex for ex in all_exchanges
            if start_date <= ex['timestamp'][:10] <= end_date
        ]
        
        return filtered[:n_results]


# Example usage (for testing):
if __name__ == "__main__":
    # Initialize memory
    memory = VectorMemory(persist_dir="./test_chroma_db")
    
    # Add some sample exchanges
    memory.add_exchange(
        "What is Python?",
        "Python is a high-level, interpreted programming language known for its simplicity."
    )
    
    memory.add_exchange(
        "How do I learn machine learning?",
        "Start with Python basics, then learn NumPy, Pandas, and scikit-learn. Practice on Kaggle."
    )
    
    memory.add_exchange(
        "Best pizza toppings?",
        "Classic pepperoni and mushrooms, or for adventurous types, pineapple! 🍕"
    )
    
    # Search for similar conversations
    print("\n" + "="*60)
    print("SEARCH: 'Tell me about Python programming'")
    print("="*60)
    
    results = memory.search_similar("Tell me about Python programming", n_results=2)
    for r in results:
        print(f"\n[Similarity: {r['similarity']:.3f}]")
        print(f"User: {r['user_message']}")
        print(f"Bot: {r['bot_response'][:100]}...")
    
    # Get formatted context
    print("\n" + "="*60)
    print("FORMATTED CONTEXT")
    print("="*60)
    context = memory.get_relevant_context("Python basics", n_results=2)
    print(context)
    
    # Show stats
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
