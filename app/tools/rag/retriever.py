from qdrant_client import models

if __package__:
	from app.tools.rag.reranker import rerank
	from app.tools.rag.vector_store import COLLECTION, client, dense, ensure_collection, sparse
else:
	from reranker import rerank
	from vector_store import COLLECTION, client, dense, ensure_collection, sparse


def search(query, limit=5):
	ensure_collection()
	dense_query = list(dense.embed([query]))[0]
	sparse_query = list(sparse.embed([query]))[0]
	results = client.query_points(
		collection_name=COLLECTION,
		prefetch=[
			models.Prefetch(query=list(dense_query), using="dense", limit=limit * 2),
			models.Prefetch(
				query=models.SparseVector(
					indices=list(sparse_query.indices), values=list(sparse_query.values)
				),
				using="sparse",
				limit=limit * 2,
			),
		],
		query=models.FusionQuery(fusion=models.Fusion.RRF),
		limit=limit,
		with_payload=True,
	)
	parents, seen = [], set()
	for point in results.points:
		payload = point.payload or {}
		parent = payload.get("parent", payload.get("text", ""))
		if parent not in seen:
			seen.add(parent)
			parents.append(payload)
	return rerank(query, parents, limit)


if __name__ == "__main__":
	import sys

	if len(sys.argv) < 2:
		print("Usage: python app/tools/rag/retriever.py <question>")
		sys.exit(1)
	for result in search(" ".join(sys.argv[1:])):
		print(result.get("parent", result.get("text", "")))
