# Building Ethical LLM Assistants

**Track:** Advanced AI/ML (Day 2)

This folder holds the **facilitator facing notes** and the **hands on code** for the session. Workshop materials (Jupyter notebook, mock responses, dependencies) live in the **`code`** subfolder here.

## Contents of this folder

**Ethical_LLM Detailed Notes.pdf**

A full session guide: learning objectives, theory modules (LLM foundations, ethical landscape, Ghana context, guardrails), facilitator teaching notes, lab sequencing, test scenarios, ethical audit template, appendices on timing and facilitation.

Use the PDF as the single source for what to say in the room, how long each block runs, and what students must submit. The notebook implements the technical path described in Part 2 of that document.

## Relationship to the `code` folder

Everything for the lab is under **`code/`** in this same directory:

**`code/ethical_llm_workshop.ipynb`** (main notebook)

**`code/workshop_mocks.py`** (imported by the notebook when `MOCK_MODE` is on)

See **`code/README.md`** for installation, Colab usage, `MOCK_MODE`, and API keys.

## Session at a glance

**Theory:** Why LLM assistants fail (hallucination, bias, consent, accountability, adversarial use), how context in Ghana changes the risk picture, and how guardrails stack (system prompt, validation, filtering, human escalation, logging).

**Lab:** Build a minimal credit access assistant for Ghana, add retrieval augmented generation over a small knowledge base, run a seven scenario battery, complete a structured ethical audit.

**Deliverable:** The ethical audit, with quoted model outputs and retrieval logs as evidence; code supports that audit.
