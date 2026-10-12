import re
import uuid
from pathlib import Path

from qdrant_client import models


if __package__:
	from app.tools.rag.vector_store import COLLECTION, client, dense, ensure_collection, sparse
else:
	from vector_store import COLLECTION, client, dense, ensure_collection, sparse


def _chunks(text, size):
	sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
	chunks, current = [], ""
	for sentence in filter(None, sentences):
		if current and len(current) + len(sentence) + 1 > size:
			chunks.append(current)
			current = ""
		current = f"{current} {sentence}".strip()
	return chunks + ([current] if current else [])


def add_text(text, source="text"):
	ensure_collection()
	parents = _chunks(text, 1400)
	children = [(parent, child) for parent in parents for child in _chunks(parent, 350)]
	texts = [child for _, child in children]
	dense_vectors = dense.embed(texts)
	sparse_vectors = sparse.embed(texts)
	points = []

	for (parent, child), dense_vector, sparse_vector in zip(children, dense_vectors, sparse_vectors):
		points.append(
			models.PointStruct(
				id=uuid.uuid4().hex,
				vector={
					"dense": list(dense_vector),
					"sparse": models.SparseVector(
						indices=list(sparse_vector.indices), values=list(sparse_vector.values)
					),
				},
				payload={"text": child, "parent": parent, "source": source},
			)
		)
	client.upsert(collection_name=COLLECTION, points=points, wait=True)


def add_file(path):
	path = Path(path)
	add_text(path.read_text(encoding="utf-8"), path.name)


def add_documents(folder="documents"):
	folder = Path(folder)
	files = [
		path for path in folder.glob("*")
		if path.is_file() and path.suffix.lower() in {".txt", ".md", ".markdown"}
	]
	for path in files:
		add_file(path)
	print(f"Added {len(files)} document(s) to Qdrant.")


if __name__ == "__main__":
	import sys

	add_documents(sys.argv[1] if len(sys.argv) > 1 else "documents")
