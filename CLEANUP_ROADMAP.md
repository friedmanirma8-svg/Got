# 🧹 Cleanup Roadmap: Got Bot Project

**Created:** January 8, 2026  
**Purpose:** Step-by-step guide to optimize repository structure

---

## 📊 Current vs. Proposed Structure

### 🔴 CURRENT STRUCTURE (Issues Highlighted)

```
my_got_bot/
│
├── main.py                        ✅ Keep
├── app_chainlit.py                ✅ Keep
├── config.py                      ✅ Keep
├── requirements.txt               ✅ Keep
├── start.sh                       ✅ Keep
│
├── inbox.py                       ⚠️  Should move to senses/
├── eyes.py                        ⚠️  Should rename to vision.py, move to senses/
├── brain.py                       ⚠️  Should move to engine/cot_linear.py
├── brain_graph.py                 ⚠️  Should move to engine/cot_graph.py
├── mouth.py                       ⚠️  Should move to expression/
│
├── README.md                      ✅ Keep (consolidate others into this)
├── ARCHITECTURE.md                ⚠️  Merge into README.md or keep as-is
├── EXAMPLES.md                    ✅ Keep
├── INSTALL.md                     ✅ Keep
├── PROJECT_SUMMARY.txt            ❌ DELETE (merge into README.md)
├── QUICKSTART.txt                 ❌ DELETE (merge into README.md)
├── chainlit.md                    ✅ Keep
│
├── .env                           ✅ Keep (but ensure in .gitignore)
├── .env.example                   ✅ Keep
├── .gitignore                     ⚠️  FIX (add __pycache__, *.pyc)
│
├── engine/
│   ├── __init__.py                ✅ Keep
│   ├── engine.py                  ⚠️  Consider renaming to reasoning.py
│   └── prompts/
│       ├── cot_initial_v2.txt     ⚠️  MOVE to /prompts/active/cot_initial.txt
│       ├── cot_refine_v2.txt      ⚠️  MOVE to /prompts/active/cot_refine.txt
│       ├── cot_initial.txt        ❌ ARCHIVE (old version)
│       └── cot_refine.txt         ❌ ARCHIVE (old version)
│
├── memory/
│   ├── __init__.py                ✅ Keep
│   ├── chat_memory.py             ✅ Keep (or rename to short_term.py)
│   ├── vector_store.py            ✅ Keep (or rename to long_term.py)
│   └── big_memory.py              ❌ DELETE (obsolete stub)
│
├── __pycache__/                   ❌ DELETE (should be in .gitignore)
│   ├── *.pyc                      ❌ DELETE ALL
│
└── .chainlit/                     ✅ Keep (Chainlit config)
    ├── config.toml
    └── translations/
```

---

### 🟢 PROPOSED STRUCTURE (Clean & Organized)

```
my_got_bot/
│
├── 🎯 ENTRY POINTS
│   ├── main.py                    # Console interface
│   └── app_chainlit.py            # Web UI interface
│
├── ⚙️ CONFIGURATION
│   ├── config.py                  # API keys, model settings
│   ├── .env                       # Active secrets (gitignored)
│   ├── .env.example               # Template
│   ├── .gitignore                 # UPDATED with __pycache__, *.pyc, chroma_db/
│   ├── requirements.txt           # Dependencies
│   └── start.sh                   # Auto-setup script
│
├── 📚 DOCUMENTATION (Consolidated)
│   ├── README.md                  # ⭐ MAIN DOC (includes quickstart, summary)
│   ├── INSTALL.md                 # Installation only
│   ├── EXAMPLES.md                # Usage examples
│   └── chainlit.md                # Chainlit welcome
│
├── 📁 engine/ - THE BRAIN (All Reasoning Logic)
│   ├── __init__.py
│   ├── reasoning.py               # Renamed from engine.py
│   ├── cot_linear.py              # Moved from brain.py (BrainText)
│   ├── cot_graph.py               # Moved from brain_graph.py (BrainGraph)
│   └── README.md                  # NEW: Explains reasoning strategies
│
├── 📁 prompts/ - PROMPT LIBRARY (Top-level, NO CODE)
│   ├── README.md                  # NEW: Prompt engineering guide
│   ├── active/
│   │   ├── cot_initial.txt        # Renamed from cot_initial_v2.txt
│   │   └── cot_refine.txt         # Renamed from cot_refine_v2.txt
│   └── archive/
│       ├── cot_initial_v1.txt     # Moved from engine/prompts/cot_initial.txt
│       └── cot_refine_v1.txt      # Moved from engine/prompts/cot_refine.txt
│
├── 📁 memory/ - MEMORY SYSTEMS
│   ├── __init__.py                # Updated exports
│   ├── short_term.py              # Renamed from chat_memory.py
│   ├── long_term.py               # Renamed from vector_store.py
│   └── README.md                  # NEW: Memory architecture
│
├── 📁 senses/ - INPUT PROCESSING
│   ├── __init__.py                # NEW
│   ├── inbox.py                   # Moved from root
│   ├── vision.py                  # Renamed from eyes.py
│   └── README.md                  # NEW: Input modalities
│
├── 📁 expression/ - OUTPUT PROCESSING
│   ├── __init__.py                # NEW
│   ├── mouth.py                   # Moved from root
│   └── README.md                  # NEW: Response formatting
│
├── 📁 tests/
│   ├── test_memory.py             # Rename from test_vector_memory.py
│   ├── test_reasoning.py          # NEW
│   ├── test_senses.py             # NEW
│   ├── test_expression.py         # NEW
│   └── test_integration.py        # NEW
│
└── 📁 .chainlit/ (Unchanged)
    ├── config.toml
    └── translations/
```

---

## 🚀 Step-by-Step Cleanup Plan

### Phase 1: IMMEDIATE CLEANUP (Required)

**Estimated Time:** 30 minutes  
**Risk:** Low  
**Impact:** High (removes clutter)

#### Step 1.1: Delete Obsolete Files

```bash
cd /workspaces/Got/my_got_bot

# Delete obsolete stub
rm memory/big_memory.py

# Remove Python cache files (should be gitignored)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

**Files Deleted:**
- ❌ `memory/big_memory.py` (replaced by vector_store.py)
- ❌ All `__pycache__/` directories
- ❌ All `*.pyc` files

#### Step 1.2: Fix .gitignore

```bash
# Add to my_got_bot/.gitignore
cat >> .gitignore << 'EOF'

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Environment
.env

# ChromaDB storage
chroma_db/
*.db

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

#### Step 1.3: Archive Old Prompts

```bash
cd /workspaces/Got/my_got_bot/engine/prompts

# Create archive directory
mkdir -p archive

# Move old versions
mv cot_initial.txt archive/cot_initial_v1.txt
mv cot_refine.txt archive/cot_refine_v1.txt

# Rename v2 to active versions
mv cot_initial_v2.txt cot_initial.txt
mv cot_refine_v2.txt cot_refine.txt
```

**Result:**
```
engine/prompts/
├── cot_initial.txt      # Active (was v2)
├── cot_refine.txt       # Active (was v2)
└── archive/
    ├── cot_initial_v1.txt
    └── cot_refine_v1.txt
```

---

### Phase 2: DOCUMENTATION CONSOLIDATION (Optional but Recommended)

**Estimated Time:** 1 hour  
**Risk:** Low  
**Impact:** Medium (easier navigation)

#### Step 2.1: Merge PROJECT_SUMMARY.txt into README.md

```bash
cd /workspaces/Got/my_got_bot

# Backup current README
cp README.md README_backup.md

# Create new consolidated README
# (Manual editing required - merge key sections)
```

**Merge Plan:**
1. Keep README.md structure
2. Add "Quick Summary" section from PROJECT_SUMMARY.txt
3. Add ASCII art banner (optional, keep it fun!)
4. Delete PROJECT_SUMMARY.txt after merge

#### Step 2.2: Merge QUICKSTART.txt into README.md

**Add to README.md:**
```markdown
## 🚀 Quick Start (60 seconds)

1. **Install:**
   ```bash
   cd my_got_bot
   pip install -r requirements.txt
   ```

2. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env and add your TOGETHER_API_KEY
   ```

3. **Run:**
   ```bash
   # Console mode
   python main.py
   
   # OR Web UI
   chainlit run app_chainlit.py -w
   ```

4. **Chat:**
   - Type questions naturally
   - Upload images/PDFs (Chainlit only)
   - Type `exit` to quit
```

**Then delete QUICKSTART.txt**

---

### Phase 3: STRUCTURAL REFACTORING (Advanced, Optional)

**Estimated Time:** 3-5 hours  
**Risk:** Medium (requires code updates)  
**Impact:** High (cleaner architecture)

⚠️ **WARNING:** This phase requires updating import statements in multiple files. Test thoroughly after each change.

#### Step 3.1: Create New Module Directories

```bash
cd /workspaces/Got/my_got_bot

# Create new directories
mkdir -p prompts/active
mkdir -p prompts/archive
mkdir -p senses
mkdir -p expression
```

#### Step 3.2: Reorganize Prompts (Separate from Code)

```bash
# Move prompts to top level
mv engine/prompts/cot_initial.txt prompts/active/
mv engine/prompts/cot_refine.txt prompts/active/
mv engine/prompts/archive/* prompts/archive/ 2>/dev/null

# Remove old prompts directory
rm -rf engine/prompts
```

**Update engine/engine.py:**

```python
# OLD:
prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

# NEW:
prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts", "active")
```

#### Step 3.3: Move Input/Output Modules

```bash
# Move input handling to senses/
mv inbox.py senses/
mv eyes.py senses/vision.py

# Move output handling to expression/
mv mouth.py expression/

# Create __init__.py files
touch senses/__init__.py
touch expression/__init__.py
```

**Update senses/__init__.py:**

```python
"""
Input processing module: Text validation and multimodal content handling.

Components:
- inbox: Text input validation, exit detection
- vision: Image processing, PDF extraction, document parsing
"""
from .inbox import get_user_message
from .vision import process_visual_content

__all__ = ['get_user_message', 'process_visual_content']
```

**Update expression/__init__.py:**

```python
"""
Output processing module: Response extraction and formatting.

Components:
- mouth: Final answer extraction, display formatting
"""
from .mouth import speak, extract_final_answer

__all__ = ['speak', 'extract_final_answer']
```

**Update main.py imports:**

```python
# OLD:
from inbox import get_user_message
from eyes import process_visual_content
from mouth import speak

# NEW:
from senses import get_user_message, process_visual_content
from expression import speak
```

#### Step 3.4: Reorganize Brain/Reasoning Modules

```bash
# Move reasoning modules to engine/
mv brain.py engine/cot_linear.py
mv brain_graph.py engine/cot_graph.py
```

**Update engine/__init__.py:**

```python
"""
Reasoning engine module: Chain-of-Thought and Graph-of-Thoughts implementations.

Components:
- reasoning: API calls, prompt loading (main inference engine)
- cot_linear: Linear Chain-of-Thought (BrainText)
- cot_graph: Tree-of-Thoughts (BrainGraph) - not yet integrated
"""
from .engine import think_one_step, load_prompt
from .cot_linear import BrainText
from .cot_graph import BrainGraph

__all__ = ['think_one_step', 'load_prompt', 'BrainText', 'BrainGraph']
```

**Update main.py imports:**

```python
# OLD:
from brain import BrainText
from engine import think_one_step

# NEW:
from engine import think_one_step, BrainText
```

#### Step 3.5: Rename Memory Files (Optional)

```bash
cd memory/

# Rename for clarity
mv chat_memory.py short_term.py
mv vector_store.py long_term.py
```

**Update memory/__init__.py:**

```python
"""
Memory module: Short-term and long-term conversation storage.

Short-term: In-memory queue of last 20 exchanges (lost on restart)
Long-term: ChromaDB vector store with semantic search (persistent)
"""
from .short_term import ChatMemory
from .long_term import VectorMemory

__all__ = ['ChatMemory', 'VectorMemory']
```

---

### Phase 4: ADD MODULE DOCUMENTATION (Recommended)

**Estimated Time:** 1-2 hours  
**Risk:** None  
**Impact:** High (better maintainability)

#### Create README.md in each module:

**engine/README.md:**

```markdown
# 🧠 Engine Module - Reasoning Logic

## Purpose
Contains all reasoning and inference logic for the bot.

## Components

### `reasoning.py` (formerly `engine.py`)
- Loads prompts from text files
- Calls Together.ai API
- Handles multimodal content (text + images)
- Manages temperature, max_tokens settings

### `cot_linear.py` (formerly `brain.py`)
- **BrainText** class: Linear Chain-of-Thought state
- Stores step-by-step reasoning as simple text chain
- Used by default in main.py

### `cot_graph.py` (formerly `brain_graph.py`)
- **BrainGraph** class: Tree-of-Thoughts structure
- Supports branching, scoring, pruning
- ⚠️ NOT YET INTEGRATED (future feature)

## Usage

```python
from engine import think_one_step, BrainText

brain = BrainText()
response = think_one_step(
    user_message="What is AI?",
    history="",
    current_cot=brain.get_chain(),
    is_first_step=True
)
brain.add_step(response)
```
```

**prompts/README.md:**

```markdown
# 📝 Prompts Module - Prompt Library

## Purpose
Stores all prompt templates separate from code for easy editing.

## Structure

- **active/** - Currently used prompts
  - `cot_initial.txt` - First iteration prompt (understanding, analysis)
  - `cot_refine.txt` - Refinement iterations (self-critique, alternatives)

- **archive/** - Old versions for reference
  - `cot_initial_v1.txt` - Original prompt
  - `cot_refine_v1.txt` - Original refinement

## Editing Prompts

1. Edit .txt files in `active/` directory
2. No code changes needed (engine.py loads from files)
3. Restart bot to apply changes
4. Archive old versions before major changes

## Prompt Structure

Each prompt uses these placeholders:
- `{relevant_context}` - Similar past conversations (from vector memory)
- `{history}` - Recent chat history (last 20 exchanges)
- `{user_message}` - Current user input
- `{current_cot}` - Chain-of-thought so far

## Best Practices

- Keep language consistent (Russian in this case)
- Include clear structure markers
- Add examples in prompts
- Test changes with edge cases
```

**memory/README.md:**

```markdown
# 💾 Memory Module - Storage Systems

## Purpose
Manages short-term and long-term conversation memory.

## Components

### `short_term.py` (formerly `chat_memory.py`)
- **ChatMemory** class
- Stores last 20 exchanges in FIFO queue
- In-memory only (lost on restart)
- Fast access, no disk I/O

### `long_term.py` (formerly `vector_store.py`)
- **VectorMemory** class
- ChromaDB vector database with semantic search
- Persistent (survives restarts)
- Uses sentence-transformers for embeddings (all-MiniLM-L6-v2)

## Usage

```python
from memory import ChatMemory, VectorMemory

# Short-term memory
chat_mem = ChatMemory(max_exchanges=20)
chat_mem.add_exchange("Hello", "Hi there!")
history = chat_mem.get_formatted_history()

# Long-term memory
vector_mem = VectorMemory(persist_dir="./chroma_db")
vector_mem.add_exchange("What is Python?", "Python is a programming language.")
context = vector_mem.get_relevant_context("Tell me about Python", n_results=3)
```

## Architecture

| Type | Storage | Persistence | Retrieval | Use Case |
|------|---------|-------------|-----------|----------|
| Short-term | In-memory list | None | Sequential | Conversation context |
| Long-term | ChromaDB | Permanent | Semantic search | Similar past exchanges |
```

**senses/README.md:**

```markdown
# 👁️ Senses Module - Input Processing

## Purpose
Handles all input modalities: text, images, documents.

## Components

### `inbox.py`
- **get_user_message()** - Console input validation
- Checks for exit commands (exit, quit, q)
- Returns None on exit, empty string on invalid

### `vision.py` (formerly `eyes.py`)
- **process_visual_content()** - Multimodal processing
- Supports:
  - Images: PNG, JPG, GIF, BMP, WEBP → base64 encoding
  - Documents: PDF → text extraction (pymupdf)
  - Documents: DOCX → text extraction (python-docx)
  - Text files: TXT → direct reading

## Usage

```python
from senses import get_user_message, process_visual_content

# Text input
user_input = get_user_message()

# File processing
content = process_visual_content("image.png")  # Returns base64 image
content = process_visual_content("doc.pdf")    # Returns extracted text
```
```

**expression/README.md:**

```markdown
# 🗣️ Expression Module - Output Processing

## Purpose
Extracts and formats bot responses for display.

## Components

### `mouth.py`
- **extract_final_answer()** - Parses model output
- **speak()** - Displays response to user

## Logic

1. Search for `FINAL_ANSWER:` marker in response
2. If found: Extract everything after marker
3. If not found: Return full response (still thinking)

## Usage

```python
from expression import speak, extract_final_answer

model_response = "Reasoning: ...\n\nFINAL_ANSWER: The answer is 42."

answer, is_final = extract_final_answer(model_response)
# answer = "The answer is 42."
# is_final = True

speak(model_response)  # Displays formatted output
```
```

---

## ✅ Verification Checklist

After each phase, verify:

### Phase 1 Checklist
- [ ] `big_memory.py` deleted
- [ ] No `__pycache__/` directories exist
- [ ] No `*.pyc` files in git
- [ ] `.gitignore` excludes `__pycache__/`, `*.pyc`, `.env`, `chroma_db/`
- [ ] Old prompts archived
- [ ] Active prompts renamed (no v2 suffix)

### Phase 2 Checklist
- [ ] README.md contains quickstart info
- [ ] PROJECT_SUMMARY.txt deleted (content merged)
- [ ] QUICKSTART.txt deleted (content merged)
- [ ] No duplicate information across docs

### Phase 3 Checklist
- [ ] `prompts/` exists at root level
- [ ] `senses/` directory created with inbox.py, vision.py
- [ ] `expression/` directory created with mouth.py
- [ ] `engine/` contains cot_linear.py, cot_graph.py
- [ ] All `__init__.py` files updated with exports
- [ ] `main.py` imports work correctly
- [ ] `app_chainlit.py` imports work correctly
- [ ] Bot runs without errors: `python main.py`
- [ ] Web UI runs: `chainlit run app_chainlit.py`

### Phase 4 Checklist
- [ ] `engine/README.md` created
- [ ] `prompts/README.md` created
- [ ] `memory/README.md` created
- [ ] `senses/README.md` created
- [ ] `expression/README.md` created
- [ ] Each README explains module purpose
- [ ] Each README includes usage examples

---

## 🧪 Testing After Changes

```bash
# 1. Syntax check
python -m py_compile main.py
python -m py_compile app_chainlit.py

# 2. Import check
python -c "from senses import get_user_message; print('✅ senses OK')"
python -c "from expression import speak; print('✅ expression OK')"
python -c "from engine import BrainText; print('✅ engine OK')"
python -c "from memory import ChatMemory, VectorMemory; print('✅ memory OK')"

# 3. Run tests
cd /workspaces/Got
pytest tests/test_vector_memory.py -v

# 4. Manual test
python my_got_bot/main.py
# Type a test question and verify response

# 5. Web UI test
chainlit run my_got_bot/app_chainlit.py -w
# Open browser and test
```

---

## 🎯 Priority Recommendations

### 🔴 HIGH PRIORITY (Do Now)
1. ✅ Delete `big_memory.py`
2. ✅ Fix `.gitignore`
3. ✅ Remove `__pycache__/`
4. ✅ Archive old prompts

### 🟡 MEDIUM PRIORITY (Do This Week)
5. ⭐ Consolidate documentation
6. ⭐ Create module READMEs

### 🟢 LOW PRIORITY (Future)
7. ⭐ Refactor directory structure (Phase 3)
8. ⭐ Rename files for clarity
9. ⭐ Integrate brain_graph.py (Tree-of-Thoughts)

---

## 📊 Before vs. After Comparison

| Metric | Before | After (Phase 1) | After (Phase 3) |
|--------|--------|-----------------|-----------------|
| **Total files** | 63 | 57 | 65 |
| **Python files** | 13 | 13 | 13 |
| **Cache files** | 6+ | 0 | 0 |
| **Obsolete files** | 3 | 0 | 0 |
| **Documentation files** | 7 | 5 | 10 (with module READMEs) |
| **Module READMEs** | 0 | 0 | 5 |
| **Redundant files** | 3 | 0 | 0 |
| **Directory depth** | 3 levels | 3 levels | 3 levels |
| **Clear module boundaries** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚨 Rollback Plan (If Something Breaks)

```bash
# Before starting, create backup
cd /workspaces/Got
cp -r my_got_bot my_got_bot_backup_$(date +%Y%m%d)

# If something breaks after Phase 3:
cd /workspaces/Got
rm -rf my_got_bot
mv my_got_bot_backup_YYYYMMDD my_got_bot

# OR use git:
git checkout -- my_got_bot/
```

---

## 📝 Notes

- **Russian Comments:** All code comments are in Russian - maintain this consistency
- **Chainlit Config:** Don't modify `.chainlit/` unless needed for UI changes
- **Tests:** Run `pytest tests/` after structural changes
- **Imports:** Update all import statements when moving files
- **.env:** Never commit to git (already in .gitignore)

---

**Last Updated:** January 8, 2026  
**Status:** ✅ Ready for execution  
**Estimated Total Time:** 5-8 hours (spread over 2-3 days)
