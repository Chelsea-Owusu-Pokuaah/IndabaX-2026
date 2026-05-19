# Architecture Diagram for Exercise 3C

The following ASCII diagram illustrates the production architecture used in Exercise 3C.

```
┌───────────────────────────────────────────────────────────────────────┐
│                         DISCORD INTERFACE                           │
│  User sends commands via Discord bot                                 │
└───────────────────────────────────────┬───────────────────────┘
                                          │ command + task description
                                          ▼
┌───────────────────────────────────────────────────────────────────────┐
│                            ORCHESTRATOR                              │
│  - Receives task from Discord                                         │
│  - Classifies task type (classifier model)                            │
│  - Selects target model and routes task                               │
│  - Manages task queue and concurrency limits                          │
│  - Reports results back to Discord                                    │
└─────────────────────┬───────────────────────────────────────┬───────────────────────┘
                      │ spawn                                │ spawn
                      ▼                                      ▼
┌───────────────┐          ┌───────────────────────┐          ┌───────────────────────┐
│   WORKER A     │          │     WORKER B            │          │   WORKER C              │
│ (Docker +       │          │ (Docker +              │          │ (Docker +               │
│  git worktree)  │          │  git worktree)         │          │  git worktree)          │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │ calls                          │ calls                          │ calls
        ▼                                ▼                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          CLAUDE CODE CLI                              │
│  Headless execution of coding tasks                                   │
│  permissionMode: approve‑all                                            │
└───────────────────────────────────────┬───────────────────────┘
                                        │ all model calls
                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                            LITELLM PROXY                            │
│  Unified model interface – routes to:                                 │
│  - Local Ollama nodes (least‑busy routing)                            │
│  - Azure Foundry (cloud fallback)                                     │
└───────┬───────────────────────┬───────────────────────┬───────────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────┐                ┌───────┐                ┌───────┐
│ 94GB  │                │ 16GB  │                │ 8GB   │
│ NODE  │                │ NODE  │                │ NODE  │
│ Qwen3 │                │DeepSeek│                │Classif│
│ Coder │                │ Coder │                │(Qwen3 │
│ (prim)│                │ /GPT‑ │                │5‑9B)  │
└───────┘                └───────┘                └───────┘
```

## Component Notes

* **Orchestrator** – Handles task lifecycle, queue management, and concurrency limits.
* **Workers** – Each runs inside Docker with its own git worktree, ensuring isolation per task.
* **Claude Code CLI** – Executes code in a headless mode with `approve‑all` permission.
* **LiteLLM** – Routes all LLM calls to local Ollama nodes or to Azure Foundry as a fallback, using least‑busy load balancing.
* **GPU Nodes** – Dedicated GPUs host the various large‑model instances (Qwen‑3‑Coder, DeepSeek/Coder, GPT‑OSS, and the classifier).

## Discussion Questions

1. Where is the single biggest reliability risk in this architecture?
2. Where would you add a human‑in‑the‑loop checkpoint, and why there specifically?
3. If you had to ship in two weeks, what would you cut and in what order?
4. Which component would fail first under a 10× load increase?
5. Where does MCP fit in this diagram? Where would A2A fit if you added it?
