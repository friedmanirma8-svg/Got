# 🎯 Integration Guide: Adding Long-Term Memory to Got Bot

This guide shows you how to integrate the new VectorMemory system into your existing bot.

## 📋 Prerequisites

Install required dependencies:
```bash
pip install chromadb sentence-transformers
```

Update your `requirements.txt`:
```bash
echo "chromadb" >> requirements.txt
echo "sentence-transformers" >> requirements.txt
```

## 🔧 Step-by-Step Integration

### Step 1: Update memory/__init__.py

Add VectorMemory to the package exports:

```python
"""
Memory system initialization.
Exports short-term (ChatMemory), long-term stub (BigMemory),
and new vector-based memory (VectorMemory).
"""

from .chat_memory import ChatMemory
from .big_memory import BigMemory
from .vector_store import VectorMemory  # NEW

__all__ = ["ChatMemory", "BigMemory", "VectorMemory"]
```

### Step 2: Update main.py

Modify the main function to use VectorMemory:

```python
from inbox import get_user_message
from eyes import process_visual_content
from memory import ChatMemory, VectorMemory  # Add VectorMemory
from brain import BrainText
from engine import think_one_step
from mouth import speak
from config import MAX_COT_ITERATIONS


def main():
    """
    Main function with integrated long-term memory.
    """
    print("\n" + "=" * 60)
    print("🤖 Chain-of-Thought Chatbot (Together.ai) + Vector Memory")
    print("=" * 60)
    print("Введите 'exit' или 'quit' для выхода\n")
    
    # Initialize components
    chat_memory = ChatMemory(max_exchanges=20)
    vector_memory = VectorMemory(persist_dir="./chroma_db")  # NEW: Long-term memory
    brain = BrainText()
    
    # Main loop
    while True:
        # 1. Get user message
        user_message = get_user_message()
        
        if user_message is None:
            print("\n👋 До свидания!")
            break
        
        if not user_message:
            continue
        
        # 2. Process visual content
        processed_message = process_visual_content(user_message)
        
        # 3. Get conversation history
        recent_history = chat_memory.get_formatted_history()
        
        # 4. NEW: Get relevant context from vector memory
        relevant_context = vector_memory.get_relevant_context(
            user_message if isinstance(user_message, str) else str(processed_message),
            n_results=3,
            min_similarity=0.3
        )
        
        print("\n" + "=" * 60)
        print("=== VECTOR MEMORY ===")
        print("=" * 60)
        print(relevant_context)
        
        # 5. Combine contexts
        full_history = f"{relevant_context}\n\n{recent_history}"
        
        # 6. Clear brain for new request
        brain.clear()
        
        # 7. Execute CoT iterations
        final_answer = None
        
        for iteration in range(1, MAX_COT_ITERATIONS + 1):
            print(f"\n🔄 Итерация {iteration}/{MAX_COT_ITERATIONS}")
            
            is_first = (iteration == 1)
            response = think_one_step(
                user_message=processed_message,
                history=full_history,  # Now includes vector context
                current_cot=brain.get_chain(),
                is_first_step=is_first
            )
            
            brain.add_step(response)
            answer, is_final = speak(response)
            
            if is_final:
                final_answer = answer
                break
        
        # Handle max iterations reached
        if final_answer is None:
            print("⚠️  Достигнут лимит итераций, беру последний ответ")
            final_answer = brain.get_chain().split("\n\n")[-1]
            print("\n" + "=" * 60)
            print("=== MOUTH (принудительно) ===")
            print("=" * 60)
            print(f"🗣️  {final_answer}\n")
        
        # 8. Save to both memories
        chat_memory.add_exchange(user_message, final_answer)
        
        # NEW: Persist to vector memory
        vector_memory.add_exchange(
            user_message if isinstance(user_message, str) else "multimodal content",
            final_answer
        )
        
        print(f"💾 Сохранено в память:")
        print(f"   - Краткосрочная: {len(chat_memory)} обменов")
        print(f"   - Долгосрочная: {vector_memory.get_stats()['total_exchanges']} обменов")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем. До свидания!")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        raise
```

### Step 3: Update engine/engine.py

Modify `think_one_step` to handle the new context structure. The function signature remains the same, but the `history` parameter now includes both recent and relevant context.

**No changes needed** - the function already accepts a formatted history string!

### Step 4: Update app_chainlit.py

Add VectorMemory to the Chainlit interface:

```python
import chainlit as cl
from eyes import process_visual_content
from memory import ChatMemory, VectorMemory  # Add VectorMemory
from brain import BrainText
from engine import think_one_step
from mouth import extract_final_answer
from config import MAX_COT_ITERATIONS
import sys
import io


# Global memory for user
chat_memory = ChatMemory(max_exchanges=20)
vector_memory = VectorMemory(persist_dir="./chroma_db")  # NEW
brain = BrainText()


class SuppressOutput:
    """Context manager to suppress console output"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


@cl.on_chat_start
async def start():
    """Initialize chat"""
    stats = vector_memory.get_stats()
    await cl.Message(
        content=f"👋 Привет! Я Chain-of-Thought бот с долгосрочной памятью.\n\n"
                f"💾 В памяти: {stats['total_exchanges']} прошлых разговоров\n\n"
                f"Задавай вопросы или загружай файлы!"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    
    # Determine input content
    if message.elements:
        file_path = message.elements[0].path
        user_input = process_visual_content(file_path)
    else:
        user_input = message.content
    
    # Clear brain
    brain.clear()
    
    # Get histories
    recent_history = chat_memory.get_formatted_history()
    
    # NEW: Get relevant context
    user_text = message.content if isinstance(message.content, str) else "multimodal"
    relevant_context = vector_memory.get_relevant_context(user_text, n_results=3)
    
    full_history = f"{relevant_context}\n\n{recent_history}"
    
    # Execute CoT iterations
    final_answer = None
    
    with SuppressOutput():
        for iteration in range(1, MAX_COT_ITERATIONS + 1):
            is_first = (iteration == 1)
            response = think_one_step(
                user_message=user_input,
                history=full_history,
                current_cot=brain.get_chain(),
                is_first_step=is_first
            )
            
            brain.add_step(response)
            answer, is_final = extract_final_answer(response)
            
            if is_final:
                final_answer = answer
                break
    
    if final_answer is None:
        final_answer = brain.get_chain().split("\n\n")[-1]
    
    # Save to both memories
    chat_memory.add_exchange(user_text, final_answer)
    vector_memory.add_exchange(user_text, final_answer)  # NEW
    
    # Send response
    await cl.Message(content=final_answer).send()
```

### Step 5: (Optional) Use Enhanced Prompts

To use the new structured prompts, update your prompt file names in `engine.py`:

```python
def think_one_step(user_message, history, current_cot, is_first_step=True):
    # Change these lines:
    # OLD:
    # prompt_file = "cot_initial.txt" if is_first_step else "cot_refine.txt"
    
    # NEW:
    prompt_file = "cot_initial_v2.txt" if is_first_step else "cot_refine_v2.txt"
    
    # Rest of function stays the same...
```

## 🧪 Testing the Integration

### Test 1: Verify Persistence

```bash
# Run bot
python main.py

# Ask a question
You: What is Python?
Bot: Python is a programming language...

# Exit
exit

# Run again
python main.py

# Ask related question
You: Tell me more about programming
# Bot should reference previous Python conversation!
```

### Test 2: Check Vector Search

```python
# In Python REPL:
from memory.vector_store import VectorMemory

memory = VectorMemory(persist_dir="./chroma_db")
stats = memory.get_stats()
print(f"Stored: {stats['total_exchanges']} exchanges")

# Search
results = memory.search_similar("Python", n_results=3)
for r in results:
    print(f"[{r['similarity']:.2f}] {r['user_message']}")
```

### Test 3: Run Unit Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
pytest tests/test_vector_memory.py -v

# With coverage
pytest tests/test_vector_memory.py --cov=memory.vector_store --cov-report=html
```

## 📊 Monitoring Memory Usage

Add this to your main loop to track memory:

```python
# After saving to memory:
stats = vector_memory.get_stats()
print(f"\n📊 Memory Stats:")
print(f"   Total conversations: {stats['total_exchanges']}")

# Optional: Show recent additions
recent = vector_memory.search_by_date_range(
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%Y-%m-%d"),
    n_results=5
)
print(f"   Today: {len(recent)} new exchanges")
```

## 🎯 Expected Behavior

### Before Integration:
```
User: What is Python?
Bot: Python is a programming language.

[Restart bot]

User: Can you tell me more about that language?
Bot: Which language? [No context]
```

### After Integration:
```
User: What is Python?
Bot: Python is a programming language.

[Restart bot]

User: Can you tell me more about that language?
Bot: You're asking about Python! It's a versatile language used for...
     [References previous conversation]
```

## 🔧 Troubleshooting

### Issue: "No module named 'chromadb'"
```bash
pip install chromadb sentence-transformers
```

### Issue: ChromaDB initialization slow
This is normal on first run (downloading embedding model ~120MB). Subsequent runs are fast.

### Issue: Too many results
Adjust `min_similarity` threshold:
```python
relevant_context = vector_memory.get_relevant_context(
    user_message,
    n_results=3,
    min_similarity=0.5  # Increase from 0.3 for stricter matching
)
```

### Issue: Want to clear memory
```python
from memory.vector_store import VectorMemory
memory = VectorMemory(persist_dir="./chroma_db")
memory.clear_all()
```

## 🚀 Next Steps

1. ✅ **Implemented**: Vector memory with ChromaDB
2. ✅ **Implemented**: Enhanced prompts with structure
3. **TODO**: Add confidence scoring to responses
4. **TODO**: Implement BrainGraph for Tree-of-Thoughts
5. **TODO**: Add async API calls for better performance

## 📚 Additional Resources

- ChromaDB docs: https://docs.trychroma.com/
- Sentence Transformers: https://www.sbert.net/
- Vector search concepts: https://www.pinecone.io/learn/vector-search/

---

**Estimated Integration Time**: 30 minutes  
**Difficulty**: Beginner-Intermediate  
**Benefits**: Persistent memory across sessions, semantic search, improved context awareness
