import os

from dotenv import load_dotenv
from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient, models

load_dotenv()

COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "ai_agent")
client = QdrantClient(
	url=os.getenv("QDRANT_URL") or os.getenv("QDRANT_CLUSTER_NAME"),
	api_key=os.getenv("QDRANT_API_KEY"),
)
dense = TextEmbedding(os.getenv("DENSE_MODEL", "BAAI/bge-small-en-v1.5"))
sparse = SparseTextEmbedding(os.getenv("SPARSE_MODEL", "Qdrant/bm25"))


def ensure_collection():
	if not client.collection_exists(COLLECTION):
		client.create_collection(
			collection_name=COLLECTION,
			vectors_config={"dense": models.VectorParams(size=384, distance=models.Distance.COSINE)},
			sparse_vectors_config={"sparse": models.SparseVectorParams(index=models.SparseIndexParams())},
		)