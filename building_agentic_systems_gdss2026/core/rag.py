import os
import json
import numpy as np
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Embedding client
_embed_client = OpenAI(
    base_url=os.getenv("EMBED_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("EMBED_API_KEY", "ollama"),
)


def embed(texts: list[str]) -> np.ndarray:
    """Embed a list of texts and return normalized embeddings.

    Args:
        texts: List of text strings to embed.

    Returns:
        2D numpy array of shape (len(texts), embedding_dim).
        Each vector is normalized to unit length (L2 norm).
    """
    response = _embed_client.embeddings.create(
        model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        input=texts,
    )
    print("text", texts)
    print("response", response)
    embeddings = np.array([e.embedding for e in response.data])
    # Normalize each vector to unit length
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
    return embeddings / norms


class VectorIndex:
    """Minimal vector index using numpy for vector math."""

    def __init__(self, index_path: str = "data/vector_index"):
        """Initialize the vector index.

        Args:
            index_path: Path to the directory for storing index files.
        """
        self.index_path = Path(index_path)
        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None
        # Attempt to load from disk if index exists
        try:
            self._load()
        except Exception:
            pass

    def add_documents(self, documents: list[dict]) -> None:
        """Add documents to the index.

        Args:
            documents: List of dict with keys: "text", "source", "metadata" (optional).
        """
        for doc in documents:
            text = doc.get("text", "")
            source = doc.get("source", "")
            metadata = doc.get("metadata", {})

            chunks = self._chunk_text(text)
            for i, chunk_text in enumerate(chunks):
                self.chunks.append({
                    "id": len(self.chunks),
                    "text": chunk_text,
                    "source": source,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "chunk_total": len(chunks),
                    },
                })

        self._rebuild_embeddings()

    def _chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
        """Split text into overlapping chunks.

        Args:
            text: The text to chunk.
            chunk_size: Number of words per chunk.
            overlap: Number of words to overlap between chunks.

        Returns:
            List of chunked text strings.
        """
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            start += chunk_size - overlap
        return chunks

    def _rebuild_embeddings(self) -> None:
        """Rebuild embeddings for all chunks."""
        if not self.chunks:
            self.embeddings = None
            return

        texts = [chunk["text"] for chunk in self.chunks]
        self.embeddings = embed(texts)

    def save(self) -> None:
        """Save the index to disk."""
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Save chunks as JSON
        with open(self.index_path / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2)

        # Save embeddings as numpy array
        if self.embeddings is not None:
            np.save(self.index_path / "embeddings.npy", self.embeddings)

    def _load(self) -> None:
        """Load the index from disk."""
        # Load chunks
        with open(self.index_path / "chunks.json", "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        # Load embeddings
        self.embeddings = np.load(self.index_path / "embeddings.npy")

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve the most similar chunks for a query.

        Args:
            query: The query string.
            top_k: Number of results to return.

        Returns:
            List of chunk dicts with an added "score" key.
        """
        if self.embeddings is None or self.embeddings.shape[0] == 0:
            return []

        # Embed query and normalize
        query_vec = embed([query])[0]

        # Compute cosine similarity (dot product of unit vectors)
        scores = self.embeddings @ query_vec

        # Get top_k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Return results with scores
        results = []
        for idx in top_indices:
            result = self.chunks[idx].copy()
            result["score"] = float(scores[idx])
            results.append(result)

        return results


def build_index(documents_dir: str = "../data/documents") -> VectorIndex:
    """Build a vector index from documents.

    Args:
        documents_dir: Directory containing .txt files.

    Returns:
        The built and saved VectorIndex.
    """
    documents = []
    doc_path = Path(documents_dir)

    for txt_file in doc_path.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()
        documents.append({
            "text": content,
            "source": txt_file.name,
            "metadata": {"filename": txt_file.name},
        })

    index = VectorIndex()
    index.add_documents(documents)
    index.save()

    return index


def load_index(index_path: str = "data/vector_index") -> VectorIndex:
    """Load a saved vector index.

    Args:
        index_path: Path to the index directory.

    Returns:
        The loaded VectorIndex.
    """
    return VectorIndex(index_path)


if __name__ == "__main__":
    # Build the index
    index = build_index()

    # Test query
    results = index.retrieve("What is the agent loop?", top_k=3)

    print(f"\nTop {len(results)} results for 'What is the agent loop?':")
    for r in results:
        print(f"\n  Score: {r['score']:.4f}")
        print(f"  Source: {r['source']}")
        print(f"  Text: {r['text'][:200]}...")