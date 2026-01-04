# 🤖 Got - Chain-of-Thought Chatbot with Long-Term Memory

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Chainlit](https://img.shields.io/badge/UI-Chainlit-green)](https://docs.chainlit.io/)
[![ChromaDB](https://img.shields.io/badge/Memory-ChromaDB-orange)](https://www.trychroma.com/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()

A modular AI chatbot with iterative Chain-of-Thought reasoning, multimodal support, and semantic long-term memory.

## 🌟 Features

### Current (v1.0)
- ✅ **Chain-of-Thought Reasoning** - Up to 4 iterative refinement steps
- ✅ **Multimodal Input** - Images (PNG, JPG), Documents (PDF, DOCX, TXT)
- ✅ **Short-Term Memory** - Last 20 conversation exchanges
- ✅ **Dual Interface** - Console (`main.py`) and Web UI (Chainlit)
- ✅ **Vision API Support** - Native Llama-4-Maverick integration

### New (v2.0 - In Development)
- ✨ **Long-Term Memory** - ChromaDB vector store with semantic search
- ✨ **Enhanced Prompts** - Structured CoT with self-critique
- ✨ **Tree-of-Thoughts** - Branching reasoning paths (BrainGraph)
- ✨ **Comprehensive Testing** - 80%+ coverage with pytest

## 📚 Documentation

| Document | Description | Status |
|----------|-------------|--------|
| **[📖 Documentation Index](README_DOCS.md)** | **Start here** - Navigation guide | ✅ |
| [🔍 Comprehensive Analysis](COMPREHENSIVE_ANALYSIS.md) | Complete codebase analysis (600+ lines) | ✅ |
| [🔧 Integration Guide](INTEGRATION_GUIDE.md) | How to add VectorMemory step-by-step | ✅ |
| [✅ Implementation Checklist](IMPLEMENTATION_CHECKLIST.md) | Actionable tasks with progress tracking | ✅ |
| [🏗️ Architecture](my_got_bot/ARCHITECTURE.md) | System design (Russian) | ✅ |
| [📝 Examples](my_got_bot/EXAMPLES.md) | Usage examples (Russian) | ✅ |

**👉 [READ DOCUMENTATION INDEX FIRST](README_DOCS.md)** for best navigation.

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd my_got_bot

# Install dependencies
pip install -r requirements.txt

# For v2.0 features (VectorMemory):
pip install chromadb sentence-transformers

# Setup API key
cp .env.example .env
# Edit .env and add your TOGETHER_API_KEY
```

### Run Console Interface

```bash
python main.py
```

### Run Web Interface

```bash
chainlit run app_chainlit.py -w
```

## 🏗️ Architecture

```
User Input
    ↓
┌─────────────┐
│   INBOX     │ ← Input validation
└──────┬──────┘
       ↓
┌─────────────┐
│    EYES     │ ← Multimodal processing (images, PDFs)
└──────┬──────┘
       ↓
┌─────────────┐
│   MEMORY    │ ← Short-term (20 msgs) + Long-term (ChromaDB)
└──────┬──────┘
       ↓
┌─────────────┐
│    BRAIN    │ ← Chain-of-Thought state (linear or graph)
└──────┬──────┘
       ↓
┌─────────────┐      ┌──────────────┐
│   ENGINE    │ ←───→│  Together.ai │
│  (4 iters)  │      │  LLama API   │
└──────┬──────┘      └──────────────┘
       ↓
┌─────────────┐
│    MOUTH    │ ← Final answer extraction
└──────┬──────┘
       ↓
   Response
```

## 📦 Project Structure

```
Got/
├── 📚 Documentation
│   ├── COMPREHENSIVE_ANALYSIS.md       # Deep analysis + proposals
│   ├── INTEGRATION_GUIDE.md            # How-to guides
│   ├── IMPLEMENTATION_CHECKLIST.md     # Task checklist
│   └── README_DOCS.md                  # Documentation index
│
├── 🤖 Application (my_got_bot/)
│   ├── main.py                         # Console interface
│   ├── app_chainlit.py                 # Web UI
│   ├── config.py                       # Configuration
│   │
│   ├── 🔧 Core Modules
│   │   ├── inbox.py                    # Input handling
│   │   ├── eyes.py                     # Multimodal processing
│   │   ├── brain.py                    # CoT state (linear)
│   │   ├── brain_graph.py              # ✨ NEW: Tree-of-Thoughts
│   │   ├── mouth.py                    # Response extraction
│   │   │
│   │   ├── engine/
│   │   │   ├── engine.py               # API calls + reasoning
│   │   │   └── prompts/
│   │   │       ├── cot_initial.txt     # Original prompts
│   │   │       ├── cot_refine.txt
│   │   │       ├── cot_initial_v2.txt  # ✨ NEW: Structured
│   │   │       └── cot_refine_v2.txt   # ✨ NEW: Self-critique
│   │   │
│   │   └── memory/
│   │       ├── chat_memory.py          # Short-term (20 msgs)
│   │       ├── big_memory.py           # Stub
│   │       └── vector_store.py         # ✨ NEW: ChromaDB
│   │
│   └── 📋 Docs (Russian)
│       ├── ARCHITECTURE.md
│       ├── EXAMPLES.md
│       └── ...
│
└── 🧪 Tests
    └── tests/
        └── test_vector_memory.py       # ✨ NEW: Unit tests
```

## 🧠 Key Components

### 1. VectorMemory (NEW! ✨)
Semantic long-term memory with ChromaDB:
```python
from memory.vector_store import VectorMemory

memory = VectorMemory(persist_dir="./chroma_db")
memory.add_exchange("What is Python?", "Python is...")

# Semantic search
results = memory.search_similar("programming languages", n_results=3)

# Get relevant context
context = memory.get_relevant_context("Python tips", n_results=3)
```

### 2. BrainGraph (NEW! ✨)
Tree-of-Thoughts reasoning:
```python
from brain_graph import BrainGraph

brain = BrainGraph(max_depth=4, max_branches=3)
root = brain.create_root("User question")

# Branch 1
child1 = brain.add_child(root, "First approach", score=0.8)

# Branch 2
child2 = brain.add_child(root, "Second approach", score=0.6)

# Get best path
best = brain.get_best_path()
print(brain.visualize())
```

### 3. Enhanced Prompts (NEW! ✨)
Structured Chain-of-Thought with patterns:
- **Understand** → What is being asked?
- **Analyze** → What do I need to know?
- **Reason** → Apply logic/analogies
- **Verify** → Check for contradictions

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=memory --cov-report=html
```

## 📊 Progress Tracking

### Phase 1: Long-Term Memory (40% Complete)
- [x] VectorMemory implementation
- [x] Enhanced prompts (v2)
- [x] Unit tests created
- [ ] Integration into main.py
- [ ] Integration into app_chainlit.py
- [ ] Documentation updates

### Phase 2: Advanced Reasoning (30% Complete)
- [x] BrainGraph implementation
- [ ] Integration with engine
- [ ] Confidence scoring
- [ ] Self-critique mechanism

### Phase 3: Production (0% Complete)
- [ ] Async API calls
- [ ] Logging infrastructure
- [ ] Configuration schema
- [ ] Docker deployment

**See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for detailed tasks.**

## 🎯 Quick Links

- **Start Development**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Understand Architecture**: [COMPREHENSIVE_ANALYSIS.md](COMPREHENSIVE_ANALYSIS.md)
- **Track Progress**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
- **Navigate Docs**: [README_DOCS.md](README_DOCS.md)

## 🛠️ Tech Stack

- **LLM**: Llama-4-Maverick-17B (Together.ai)
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Web UI**: Chainlit
- **Vision**: PyMuPDF, python-docx, Pillow
- **Testing**: pytest, pytest-cov

## 📈 Roadmap

- **v1.0** (Current): Basic CoT + multimodal support
- **v2.0** (In Progress): Vector memory + enhanced prompts
- **v3.0** (Planned): Tree-of-Thoughts + async operations
- **v4.0** (Future): Multi-agent system + web search

## 🤝 Contributing

1. Read [COMPREHENSIVE_ANALYSIS.md](COMPREHENSIVE_ANALYSIS.md)
2. Pick a task from [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
3. Follow [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) patterns
4. Write tests (aim for 80%+ coverage)
5. Update documentation

## 📝 License

[Your License Here]

## 🙏 Acknowledgments

- Together.ai for LLM API
- ChromaDB team
- Chainlit framework
- Sentence-Transformers project

---

**Status**: Active Development  
**Last Updated**: 2026-01-04  
**Maintainer**: [Your Name/Team]

**⭐ Star this repo if you find it useful!**