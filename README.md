# ArXiv Research Agent

An agentic research-paper analysis system built with **LangGraph**. The agent retrieves research papers from arXiv, allows users to interactively select relevant papers, downloads and parses their PDFs, chunks the extracted text, generates semantic embeddings, stores them in ChromaDB, and uses a local Ollama LLM to generate an executive research briefing.

The system is designed as a modular research workflow and is being extended toward a grounded Retrieval-Augmented Generation (RAG) research assistant.

---

## Overview

The agent accepts either:

- A research topic
- A specific arXiv ID

For topic-based searches, the agent retrieves a pool of relevant papers and provides an interactive selection interface:

```text
1,3      → select papers
more     → show another batch
refine   → modify the research query
quit     → exit
```

Once papers are selected, they are downloaded, parsed, chunked, embedded, indexed in ChromaDB, and passed to a local Ollama model for executive briefing generation.

---

## Architecture

```text
                         USER INPUT
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Query Understanding │
                  └──────────┬──────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                  Topic             arXiv ID
                    │                 │
                    ▼                 ▼
              arXiv Search       Fetch Paper
                    │                 │
                    └────────┬────────┘
                             ▼
                    Paper Selection
                             │
                             ▼
                      PDF Download
                             │
                             ▼
                      PDF Parsing
                             │
                             ▼
                        Chunking
                             │
                             ▼
                   Semantic Embeddings
                             │
                             ▼
                        ChromaDB
                             │
                             ▼
                  Executive Briefing
                             │
                             ▼
                         Ollama
                             │
                             ▼
                           END
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Agent orchestration | LangGraph |
| Paper retrieval | arXiv Python API |
| HTTP requests | Requests |
| PDF parsing | PyMuPDF |
| Embeddings | Sentence Transformers |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| Local LLM runtime | Ollama |
| LLM | `llama3.1:8b` |

---

## Project Structure

```text
arxiv-research-agent/
│
├── app/
│   ├── __init__.py
│   ├── state.py
│   ├── graph.py
│   │
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── retrieval.py
│   │   ├── download.py
│   │   ├── parsing.py
│   │   ├── chunking.py
│   │   ├── indexing.py
│   │   ├── summarization.py
│   │   └── qa.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── arxiv_service.py
│       ├── pdf_service.py
│       ├── embedding_service.py
│       ├── vector_store.py
│       └── llm_service.py
│
├── data/
│   ├── papers/
│   └── chroma/
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# Workflow

## 1. Query Understanding

The initial user input is classified as either:

- `topic`
- `paper`

An arXiv-style identifier such as:

```text
2412.15998
```

is treated as a specific paper request.

Other input is treated as a research topic.

---

## 2. Topic-Based Search

For a topic query, the agent searches arXiv and retrieves a pool of candidate papers.

Example:

```text
Research topic or arXiv ID:
CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation
```

The agent displays the first batch of results:

```text
--- Papers Found ---

[1] CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation
[2] A Hybrid CNN-LSTM Approach for Laser Remaining Useful Life Prediction
[3] Learn to Accumulate Evidence from All Training Samples
[4] The Modern Mathematics of Deep Learning
[5] ...
```

---

## 3. Interactive Paper Selection

The retrieval stage supports four commands:

```text
1,3      → select papers
more     → show another batch
refine   → modify the research query
quit     → exit
```

### Select Papers

```text
> 1,3
```

selects papers 1 and 3 for further processing.

### Show More

```text
> more
```

displays the next batch of papers from the current search pool.

### Refine Search

```text
> refine

Current query: machine learning

New research query: machine learning predictive maintenance
```

The agent performs a new arXiv search using the refined query.

### Quit

```text
> quit
```

cancels the current research session.

---

# 4. Direct arXiv ID Retrieval

The user can bypass topic search by providing an arXiv ID:

```text
Research topic or arXiv ID: 2412.15998
```

The agent retrieves the specific paper directly from arXiv.

Both topic-based selection and direct paper retrieval converge to the same state representation:

```python
selected_papers
```

This allows the downstream processing pipeline to remain identical.

---

# 5. PDF Download

Selected papers are downloaded locally into:

```text
data/papers/
```

Example:

```text
data/papers/2412.15998v1.pdf
```

The download service stores the local PDF path together with the paper metadata.

---

# 6. PDF Parsing

PyMuPDF is used to extract text from downloaded PDFs.

Example:

```text
[PARSE] Parsed:
CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation
(45843 characters)
```

Each parsed paper retains its source metadata:

```python
{
    "arxiv_id": "2412.15998v1",
    "title": "CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation",
    "text": "..."
}
```

---

# 7. Text Chunking

Long paper text is divided into smaller overlapping chunks.

Current configuration:

```python
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
```

Each chunk retains information about its source paper:

```python
{
    "arxiv_id": "2412.15998v1",
    "title": "CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation",
    "chunk_id": 17,
    "text": "..."
}
```

This metadata allows retrieved information to be traced back to its original paper.

---

# 8. Semantic Embeddings

Each chunk is converted into a numerical vector using the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The process is:

```text
Paper Chunk
     │
     ▼
Sentence Transformer
     │
     ▼
Embedding Vector
```

The embedding model represents the semantic meaning of the text numerically.

This allows semantically similar text to be retrieved even when the exact wording differs.

The model is loaded once per Python process and reused for subsequent embedding operations.

Model weights are cached locally after the initial download.

---

# 9. Vector Database

The generated embeddings, text chunks, and metadata are stored in ChromaDB.

Persistent storage:

```text
data/chroma/
```

Collection:

```text
research_papers
```

Each indexed chunk contains:

- Chunk text
- Embedding vector
- arXiv ID
- Paper title
- Chunk ID

Conceptually:

```text
Paper
  ↓
Text Chunks
  ↓
Embedding Vectors
  ↓
ChromaDB
```

ChromaDB is responsible for semantic similarity search over the indexed research material.

---

# 10. Executive Research Briefing

After indexing, the selected papers are passed to the briefing node.

The briefing node extracts bounded excerpts from each paper and sends them to the local Ollama model.

The LLM is instructed to provide:

1. Research problem
2. Method
3. Main findings
4. Limitations
5. Important technical contribution
6. Cross-paper comparison
7. Research gaps
8. Further research directions

The prompt explicitly instructs the model to use only the supplied paper content and avoid inventing unsupported results.

---

# 11. Local LLM

Ollama is used to run the generative model locally.

Current model:

```text
llama3.1:8b
```

The embedding model, vector database, and LLM have separate responsibilities:

```text
Sentence Transformer
        │
        │ Converts text into numerical representations
        ▼
     ChromaDB
        │
        │ Stores and retrieves relevant chunks
        ▼
      Ollama
        │
        │ Generates natural-language responses
        ▼
      Answer
```

### Sentence Transformer

Converts paper text into embeddings that represent semantic meaning.

### ChromaDB

Stores those embeddings and retrieves the chunks most relevant to a query.

### Ollama

Uses the supplied research context to generate the final natural-language briefing or answer.

---

# LangGraph Architecture

The current LangGraph workflow is:

```text
START
  │
  ▼
query_understanding
  │
  ├────────────── topic ────────────────┐
  │                                     ▼
  │                              search_arxiv
  │                                     │
  │                                     ▼
  │                            select_topic_paper
  │                                     │
  │                                     │
  └────────────── paper ───────► fetch_paper
                                        │
                                        ▼
                                download_papers
                                        │
                                        ▼
                                  parse_papers
                                        │
                                        ▼
                                  chunk_papers
                                        │
                                        ▼
                                  index_chunks
                                        │
                                        ▼
                                    briefing
                                        │
                                        ▼
                                       END
```

The graph uses an explicit shared `AgentState` to pass information between nodes.

---

# Agent State

The shared state contains information such as:

```python
user_query
query_type
normalized_query

arxiv_results
search_pool
shown_count

selected_papers
downloaded_papers
parsed_papers

chunks
vector_collection

retrieved_chunks

briefing

current_question
current_answer
qa_history

error
```

This makes the intermediate data flowing through the agent explicit and inspectable.

---

# Retrieval-Augmented Generation

The vector database provides the foundation for the interactive research Q&A system.

The intended Q&A workflow is:

```text
User Question
      │
      ▼
Question Embedding
      │
      ▼
ChromaDB Similarity Search
      │
      ▼
Relevant Paper Chunks
      │
      ▼
Ollama
      │
      ▼
Grounded Answer
      │
      ▼
Source References
```

For example:

```text
> What dataset did the authors use?
```

The question is converted into an embedding using the same Sentence Transformer model.

ChromaDB then retrieves the most semantically relevant paper chunks.

Those chunks are provided to Ollama together with the question.

The LLM generates an answer using the retrieved evidence.

---

# Example Run

```text
Research topic or arXiv ID: 2412.15998

[DOWNLOAD] Downloaded:
CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation

[PARSE] Parsed:
CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation
(45843 characters)

[CHUNK] CNN-LSTM Hybrid Deep Learning Model for Remaining Useful Life Estimation:
46 chunks

[EMBED] Generating embeddings for 46 chunks...

[VECTOR] Indexed 46 chunks into 'research_papers'

[BRIEFING] Starting executive briefing...

[OLLAMA] Model: llama3.1:8b
[OLLAMA] Generating response...
[OLLAMA] Response received.

[BRIEFING] Ollama returned the briefing.
```

---

# Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install and start Ollama, then pull the configured model:

```bash
ollama pull llama3.1:8b
```

Verify the model:

```bash
ollama list
```

---

# Running the Agent

Start the CLI:

```bash
python main.py
```

Then enter either a research topic:

```text
CNN-LSTM remaining useful life estimation
```

or a specific arXiv ID:

```text
2412.15998
```

---

# Current Capabilities

- [x] Topic-based arXiv search
- [x] Direct arXiv ID lookup
- [x] Interactive paper selection
- [x] Multiple paper selection
- [x] Additional search batches
- [x] Query refinement
- [x] PDF downloading
- [x] PDF text extraction
- [x] Text chunking
- [x] Semantic embeddings
- [x] Persistent ChromaDB vector store
- [x] Local Ollama LLM
- [x] Executive research briefing
- [ ] Interactive grounded Q&A
- [ ] Source-aware citations in answers
- [ ] Conversation-aware follow-up questions
- [ ] Web-based frontend

---

# Design Principles

## Modular Architecture

External functionality is separated into dedicated services for:

- arXiv retrieval
- PDF downloading
- PDF parsing
- embeddings
- vector storage
- LLM generation

This keeps individual components independently testable.

## Explicit Agent State

LangGraph uses a shared `AgentState` to make information flowing between nodes explicit.

## Grounded Generation

The LLM is instructed to base research outputs on the provided paper content and avoid unsupported claims.

## Local Inference

The generative model runs locally through Ollama, avoiding dependence on a paid external LLM API for the core research workflow.

## Source Traceability

Paper IDs, titles, and chunk metadata are preserved throughout the pipeline so retrieved information can be associated with its original paper.

---

# Future Improvements

- Interactive RAG question-answering
- Source citations for generated answers
- Better section-aware PDF parsing
- Improved chunking strategies
- Retrieval ranking and filtering
- Cross-paper comparison
- Follow-up research questions
- Persistent research sessions
- Exportable research briefings
- FastAPI backend
- Web-based research interface

---

# Current Status

The current implementation has a working end-to-end ingestion and briefing pipeline:

```text
arXiv
  ↓
Paper Selection
  ↓
PDF Download
  ↓
PDF Parsing
  ↓
Chunking
  ↓
Embeddings
  ↓
ChromaDB
  ↓
Ollama
  ↓
Executive Briefing
```

The next major component is the interactive:

```text
Question
   ↓
Embedding
   ↓
ChromaDB Retrieval
   ↓
Relevant Chunks
   ↓
Ollama
   ↓
Grounded Answer + Sources
```