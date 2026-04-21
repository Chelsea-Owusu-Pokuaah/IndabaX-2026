# Building Ethical LLM Assistants: workshop code

**Track:** Advanced AI/ML (Day 2)

This folder contains everything needed to run the **hands on lab**: one notebook, offline mock completions, optional notebook rebuild script, and dependency list. Facilitator theory, timings, and audit rubric are in the PDF in the **parent** folder.

## Where to find the PDF

From this `code` directory, the detailed notes are one level up:

`../Ethical_LLM Detailed Notes.pdf`

For an overview of the PDF and how it connects to this lab, see **`../README.md`**.

## Files in this folder

**ethical_llm_workshop.ipynb**

Main lab. Run cells from top to bottom. Sections cover configuration, the base assistant, the knowledge base and retrieval, the RAG assistant, the seven scenario battery, a sample retrieval log, an audit template you can copy into your writeup, and optional bias probes.

**workshop_mocks.py**

When `MOCK_MODE = True` in the notebook, assistant replies come from this module so you can finish the audit without calling the Anthropic API. Retrieval still runs in the notebook so document ids in the logs match the teaching implementation.

**build_notebook.py**

Optional. Regenerates `ethical_llm_workshop.ipynb` from the same source structure. You do not need it to teach the class.

**requirements.txt**

Python packages for local Jupyter.

## Local setup

From this repository, open a terminal in **this** folder (the path ends with `Building Ethical LLM Assistants/code`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook ethical_llm_workshop.ipynb
```

On Windows, activate with `.venv\Scripts\activate`.

## API key and MOCK_MODE

**MOCK_MODE = True (default):** no API key. Suitable for classrooms with unreliable keys or connectivity.

**MOCK_MODE = False:** set the environment variable `ANTHROPIC_API_KEY` to your key. Never commit keys or paste them into shared documents.

## Google Colab

Upload **`ethical_llm_workshop.ipynb`** and **`workshop_mocks.py`** into the same session folder so `import workshop_mocks` works. Alternatively clone the repository and open the notebook from **`Building Ethical LLM Assistants/code`**.
