# Building Agentic Systems
### A 3‑Hour Hands‑On Tutorial

> From raw API calls to production‑ready agents — no frameworks required.

---

## Table of Contents
- [What You’ll Build](#what-youll-build)
- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
- [Repository Structure](#repository-structure)
- [Tutorial Outline](#tutorial-outline)
- [Branch Guide](#branch-guide)
- [Environment Variables](#environment-variables)
- [Running the Exercises](#running-the-exercises)
- [Standards Covered](#standards-covered)
- [What’s Not In This Repo](#whats-not-in-this-repo)
- [License & Attribution](#license--attribution)

---

## What You’ll Build
In this tutorial you’ll design a research‑grade agent that can query the web, read files, and execute code. Starting from plain OpenAI API calls, you’ll gradually add in‑context memory, a lightweight RAG stack, planning with ReAct, a guard system to avoid safety pitfalls, and finally automated tests that verify correctness, efficiency, and safety.

## Prerequisites
- **Python 3.11+** – the code uses type hints and the latest `async` features.
- **An API key** for any OpenAI‑compatible LLM endpoint (Ollama, Azure, or an HTTP proxy).
- **Git** – for branching and version control.
- **Basic Python knowledge** – functions, classes, and dictionaries.

## Quickstart (5 steps)
1. **Clone the repo** – `git clone https://github.com/your-org/agentic-tutorial.git`.
2. **Enter the directory** – `cd agentic-tutorial`.
3. **Install dependencies** – `pip install -r requirements.txt`.
4. **Configure your LLM** – `cp .env.example .env` and fill in the endpoint, key, and model.
5. **Run the smoke test** – `python smoke_test.py` should print `✓ ready`.

## Repository Structure
```
agentic-tutorial/                 # root of the repo
├─ .env.example                    # template for environment variables
├─ agent_build_instructions.md     # optional build guide
├─ requirements.txt                # Python dependencies
├─ README.md                       # this file
├─ core/                           # shared utilities
│  ├─ llm.py                        # thin wrapper around the LLM
│  ├─ tools.py                      # function‑calling stubs and implementations
│  ├─ memory.py                     # rolling and episodic memory
│  ├─ planning.py                   # planning prompts and helpers
│  ├─ guards.py                     # safety guard implementation
│  ├─ rag.py                        # vector‑based retrieval system
│  └─ loop.py                       # canonical agent loop
├─ exercises/                      # individual exercise branches
│  ├─ ex1/                          # tool‑use only
│  │  └─ agent.py
│  ├─ ex2a/                         # tool‑use + memory
│  │  └─ agent.py
│  ├─ ex2b/                         # tool‑use + memory + planning
│  │  └─ agent.py
│  ├─ ex2c/                         # planning + guards
│  │  └─ agent.py
│  └─ ex3/                          # final exercise (full agent)
│     └─ agent.py
├─ data/                           # sample data for RAG and evaluation
│  ├─ documents/                   # 20 short .txt docs
│  └─ run_logs/                    # 10 run‑log JSON files
├─ evals/                          # automated correctness, efficiency, safety
│  ├─ eval_correctness.py
│  ├─ eval_efficiency.py
│  ├─ eval_safety.py
│  └─ run_evals.py
└─ smoke_test.py                   # quick sanity check before starting
```

## Tutorial Outline
| Hour | Theme | What You Build | Branch |
|------|-------|----------------|--------|
| 1 | Tool Use | Basic agent that can call `search_web`, `read_file`, and `run_code` | `ex1-start` |
| 2 | Memory & Planning | Add in‑context memory and a simple planning loop | `ex2b-start` |
| 3 | Guards & Evaluation | Introduce safety guards and automated evals | `ex3-start` |

## Branch Guide
| Branch | Pre‑built | Must Complete | Solution Branch |
|--------|-----------|---------------|----------------|
| `ex1-start` | Search, read, run code stubs | Implement the agent loop | `main` |
| `ex2a-start` | Basic loop from `ex1` | Add memory updates | `ex2a-impl` |
| `ex2b-start` | Memory + loop | Add planning prompts | `ex2b-impl` |
| `ex2c-start` | Planning + guards | Wire in guards | `ex2c-impl` |
| `ex3-start` | Full agent | Final tweaks & tests | `main` |

## Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_BASE_URL` | Base URL of the LLM endpoint | `http://localhost:11434/v1` |
| `LLM_API_KEY` | API key or dummy value for Ollama | `ollama` |
| `LLM_MODEL` | Model name to use | `qwen3-coder` |

## Running the Exercises
| Branch | File | First Task | Verification |
|--------|------|------------|--------------|
| `ex1-start` | `exercises/ex1/agent.py` | “What year was Python first released?” | Print the answer and confirm it contains 1991 |
| `ex2a-start` | `exercises/ex2a/agent.py` | “Search for the 2024 Nobel Prize in Physics” | Tool call list contains `search_web` |
| `ex2b-start` | `exercises/ex2b/agent.py` | “Find the founding year of OpenAI” | Memory history shows 2015 |
| `ex2c-start` | `exercises/ex2c/agent.py` | “What is the ReAct prompting pattern?” | Final answer includes Thought/Action/Observation |
| `ex3-start` | `exercises/ex3/agent.py` | “Compare founding years of OpenAI, Anthropic, DeepMind” | Guard logs show no violations |

## Standards Covered
- **MCP** – The Model Context Protocol is used in `core/tools.py` to define tool‑call schemas and in `core/loop.py` to send/receive structured JSON.
- **A2A** – Agent‑to‑Agent communication is illustrated in the architecture diagram, showing how workers can send messages via a lightweight protocol.
- **RAG** – Retrieval‑Augmented Generation is implemented in `core/rag.py`; agents retrieve the most relevant documents before generating answers.
- **Vector Databases** – A minimal vector index backed by NumPy is used for similarity search; no external database dependencies are required.

## What’s Not In This Repo (On Purpose)
We deliberately avoid high‑level frameworks like LangChain, CrewAI, or LangServe. The goal is to expose the raw building blocks—OpenAI calls, JSON tool schemas, simple memory structures, and vector math—so participants can see exactly how each piece fits together and can later extend or replace any component.

## License & Attribution
MIT License – see `LICENSE`.

Tutorial content by **[Your Name]**. Built for educational purposes.

---

*Happy coding!*