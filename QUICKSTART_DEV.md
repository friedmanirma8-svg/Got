# ⚡ Quick Start Guide for Developers

**Time required**: 30-60 minutes  
**Difficulty**: Intermediate  
**Goal**: Get the enhanced bot running with vector memory

---

## 🎯 What You'll Accomplish

By the end of this guide, you'll have:
- ✅ Long-term memory with semantic search (ChromaDB)
- ✅ Enhanced structured prompts
- ✅ Working tests
- ✅ Bot that remembers conversations across restarts

---

## 📋 Prerequisites

```bash
# Check Python version (need 3.7+)
python --version

# Check pip
pip --version

# You should have:
cd /workspaces/Got/my_got_bot
```

---

## 🚀 Step 1: Install Dependencies (5 min)

```bash
# Navigate to project
cd /workspaces/Got/my_got_bot

# Install base requirements
pip install -r requirements.txt

# Install new dependencies for v2.0
pip install chromadb sentence-transformers pytest pytest-cov

# Verify installation
python -c "import chromadb; print('✅ ChromaDB installed')"
python -c "import sentence_transformers; print('✅ Sentence-Transformers installed')"
```

---

## 🔧 Step 2: Update memory/__init__.py (2 min)

Open `my_got_bot/memory/__init__.py` and replace contents with:

```python
"""
Memory system initialization.
Exports short-term (ChatMemory), long-term stub (BigMemory),
and new vector-based memory (VectorMemory).
"""

from .chat_memory import ChatMemory
from .big_memory import BigMemory
from .vector_store import VectorMemory

__all__ = ["ChatMemory", "BigMemory", "VectorMemory"]
```

Test it:
```bash
python -c "from memory import VectorMemory; print('✅ Import works')"
```

---

## 🧪 Step 3: Run Tests (5 min)

```bash
# Navigate to project root
cd /workspaces/Got

# Run vector memory tests
pytest tests/test_vector_memory.py -v

# Expected output: All tests passing ✅
```

If tests fail, check:
- ChromaDB installed correctly
- sentence-transformers installed
- Python 3.7+

---

## 🤖 Step 4: Test VectorMemory Standalone (5 min)

```bash
cd /workspaces/Got/my_got_bot

# Create test script
cat > test_memory.py << 'EOF'
from memory.vector_store import VectorMemory

# Initialize
memory = VectorMemory(persist_dir="./test_chroma_db")

# Add conversations
memory.add_exchange("What is Python?", "Python is a programming language.")
memory.add_exchange("How to learn ML?", "Start with Python, NumPy, and Pandas.")
memory.add_exchange("Best pizza?", "Margherita!")

# Search
results = memory.search_similar("Python programming", n_results=2)

print("\n✅ Search Results:")
for r in results:
    print(f"[{r['similarity']:.2f}] {r['user_message']}")

# Get context
context = memory.get_relevant_context("programming tips", n_results=2)
print("\n✅ Formatted Context:")
print(context)

# Stats
print("\n✅ Stats:")
print(memory.get_stats())
EOF

# Run test
python test_memory.py

# Cleanup
rm test_memory.py
rm -rf test_chroma_db
```

---

## 🔌 Step 5: Integrate into main.py (10 min)

Open `my_got_bot/main.py` and make these changes:

### Change 1: Add import
```python
# At top of file, change:
from memory import ChatMemory, BigMemory

# To:
from memory import ChatMemory, VectorMemory
```

### Change 2: Initialize VectorMemory
```python
# In main() function, change:
chat_memory = ChatMemory(max_exchanges=20)
big_memory = BigMemory()  # Пока не используется
brain = BrainText()

# To:
chat_memory = ChatMemory(max_exchanges=20)
vector_memory = VectorMemory(persist_dir="./chroma_db")  # NEW
brain = BrainText()
```

### Change 3: Get relevant context
```python
# After "# 3. Получаем историю диалога из памяти"
history = chat_memory.get_formatted_history()

# Add:
# 3b. Получаем релевантный контекст из долгосрочной памяти
user_text = user_message if isinstance(user_message, str) else "multimodal content"
relevant_context = vector_memory.get_relevant_context(user_text, n_results=3)

print("\n" + "=" * 60)
print("=== VECTOR MEMORY ===")
print("=" * 60)
print(relevant_context)

# Combine contexts
full_history = f"{relevant_context}\n\n{history}"
```

### Change 4: Update think_one_step call
```python
# Change:
response = think_one_step(
    user_message=processed_message,
    history=history,  # OLD
    current_cot=brain.get_chain(),
    is_first_step=is_first
)

# To:
response = think_one_step(
    user_message=processed_message,
    history=full_history,  # NEW: includes vector context
    current_cot=brain.get_chain(),
    is_first_step=is_first
)
```

### Change 5: Save to vector memory
```python
# After "# 7. Сохраняем обмен в память"
chat_memory.add_exchange(user_message, final_answer)

# Add:
vector_memory.add_exchange(user_text, final_answer)

# Update print statement:
print(f"💾 Сохранено в память:")
print(f"   Краткосрочная: {len(chat_memory)} обменов")
print(f"   Долгосрочная: {vector_memory.get_stats()['total_exchanges']} обменов")
```

---

## ✅ Step 6: Test Console Bot (10 min)

```bash
# Make sure you have API key
cat .env
# Should have: TOGETHER_API_KEY=your_key_here

# Run bot
python main.py
```

**Test conversation:**
```
You: What is Python?
Bot: [Gives answer about Python]

You: exit

# Run again
python main.py

You: Tell me more about that programming language
Bot: [Should reference Python from previous session!]
```

If it works, you should see:
```
=== VECTOR MEMORY ===
============================================================
=== RELEVANT PAST CONVERSATIONS ===

[1] Similarity: 0.89 | 2026-01-04
    User: What is Python?
    Assistant: Python is a programming language...
```

---

## 🌐 Step 7: Integrate into Chainlit (Optional, 10 min)

Open `my_got_bot/app_chainlit.py` and make similar changes:

### Change 1: Import VectorMemory
```python
from memory import ChatMemory, VectorMemory
```

### Change 2: Initialize globally
```python
# After chat_memory:
chat_memory = ChatMemory(max_exchanges=20)
vector_memory = VectorMemory(persist_dir="./chroma_db")
brain = BrainText()
```

### Change 3: Update on_chat_start
```python
@cl.on_chat_start
async def start():
    stats = vector_memory.get_stats()
    await cl.Message(
        content=f"👋 Привет! Я Chain-of-Thought бот с долгосрочной памятью.\n\n"
                f"💾 В памяти: {stats['total_exchanges']} прошлых разговоров\n\n"
                f"Задавай вопросы!"
    ).send()
```

### Change 4: Update main message handler
```python
@cl.on_message
async def main(message: cl.Message):
    # ... existing code ...
    
    # Get histories
    history = chat_memory.get_formatted_history()
    
    # NEW: Get vector context
    user_text = message.content if isinstance(message.content, str) else "multimodal"
    relevant_context = vector_memory.get_relevant_context(user_text, n_results=3)
    full_history = f"{relevant_context}\n\n{history}"
    
    # Use full_history in think_one_step
    # ... rest of code ...
    
    # Save to both memories
    chat_memory.add_exchange(user_text, final_answer)
    vector_memory.add_exchange(user_text, final_answer)  # NEW
```

### Test Chainlit:
```bash
chainlit run app_chainlit.py -w
# Open browser to http://localhost:8000
```

---

## 🎨 Step 8: (Optional) Use Enhanced Prompts (5 min)

Open `my_got_bot/engine/engine.py`:

Find this line:
```python
prompt_file = "cot_initial.txt" if is_first_step else "cot_refine.txt"
```

Change to:
```python
prompt_file = "cot_initial_v2.txt" if is_first_step else "cot_refine_v2.txt"
```

This enables structured prompts with:
- Explicit reasoning steps (Understand → Analyze → Reason → Verify)
- Self-critique mechanism
- Example-driven reasoning

---

## 🔍 Step 9: Verify Everything Works (5 min)

### Check 1: Memory persistence
```bash
# In Python REPL:
python
>>> from memory.vector_store import VectorMemory
>>> m = VectorMemory('./chroma_db')
>>> stats = m.get_stats()
>>> print(f"Stored: {stats['total_exchanges']} conversations")
>>> exit()
```

### Check 2: Search quality
```bash
python
>>> from memory.vector_store import VectorMemory
>>> m = VectorMemory('./chroma_db')
>>> results = m.search_similar("programming", n_results=3)
>>> for r in results:
...     print(f"[{r['similarity']:.2f}] {r['user_message']}")
>>> exit()
```

### Check 3: Run full test suite
```bash
cd /workspaces/Got
pytest tests/ -v --tb=short
```

---

## 🎉 Success Checklist

You should now have:
- ✅ ChromaDB installed and working
- ✅ VectorMemory class integrated
- ✅ Console bot using long-term memory
- ✅ (Optional) Chainlit using long-term memory
- ✅ (Optional) Enhanced prompts active
- ✅ All tests passing

---

## 🐛 Troubleshooting

### Error: "No module named 'chromadb'"
```bash
pip install chromadb sentence-transformers
```

### Error: ChromaDB initialization slow (first run)
**Normal!** First run downloads embedding model (~120MB). Subsequent runs are fast.

### Error: "collection already exists"
```bash
# Clear and restart
rm -rf chroma_db
python main.py
```

### Search returns no results
- Check that you've added conversations first
- Lower `min_similarity` threshold:
  ```python
  relevant_context = vector_memory.get_relevant_context(
      user_text, 
      n_results=3,
      min_similarity=0.1  # Lower threshold
  )
  ```

### Bot doesn't remember past conversations
- Verify vector_memory.add_exchange() is called after each exchange
- Check chroma_db/ directory exists and has data:
  ```bash
  ls -lh chroma_db/
  ```

---

## 📊 Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| First initialization | ~30 seconds | Downloads embedding model |
| Subsequent starts | <2 seconds | Model cached |
| Add exchange | ~50ms | Fast embedding generation |
| Search (1000 conversations) | ~100ms | Optimized vector search |
| Search (10k conversations) | ~300ms | Still fast! |

---

## 🎯 Next Steps

Now that you have long-term memory working:

1. **Test extensively**: Have real conversations, restart bot, verify memory
2. **Tune similarity threshold**: Adjust `min_similarity` for your use case
3. **Add more features**: Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
4. **Optimize prompts**: Experiment with prompt variations
5. **Add monitoring**: Track memory size, search quality

---

## 🔗 Related Resources

- **Full Analysis**: [COMPREHENSIVE_ANALYSIS.md](COMPREHENSIVE_ANALYSIS.md)
- **Detailed Integration**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Task List**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
- **Documentation Index**: [README_DOCS.md](README_DOCS.md)

---

## 💬 Questions?

Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) Troubleshooting section, or review the comprehensive analysis.

---

**Time spent**: ~45 minutes  
**Result**: Fully functional bot with long-term semantic memory! 🎉

**Next challenge**: Implement Tree-of-Thoughts reasoning with `brain_graph.py`
