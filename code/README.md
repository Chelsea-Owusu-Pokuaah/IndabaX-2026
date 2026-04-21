# Building Ethical LLM Assistants (workshop code)

This folder supports **Advanced AI/ML, Day 2**: a base credit access assistant, a retrieval augmented variant, a seven scenario test battery, and an ethical audit.

## Files

**ethical_llm_workshop.ipynb:** main notebook. Run top to bottom.

**workshop_mocks.py:** canned assistant replies when `MOCK_MODE = True`.

**build_notebook.py:** optional maintainer script to regenerate the notebook from source.

**requirements.txt:** Python dependencies.

Facilitator facing notes and theory content are in the PDF beside this folder:

`../Building Ethical LLM Assistants/Ethical_LLM Detailed Notes.pdf`

## Local setup

```bash
cd code
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook ethical_llm_workshop.ipynb
```

Set `MOCK_MODE = False` and export `ANTHROPIC_API_KEY` only in a trusted environment.

## Google Colab

Upload `ethical_llm_workshop.ipynb` and `workshop_mocks.py` into the same Colab session directory, or clone this repository and open the notebook from the `code` folder so imports succeed.
