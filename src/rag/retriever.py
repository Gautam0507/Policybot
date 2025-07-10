import chromadb
import numpy as np
from torch import _load_global_deps, flatten

from src.config import cfg
from src.logger import logger
from src.util import free_embedding_model, load_embedding_model


class Retriever:
    def __init__(self, top_k=5):
        self.chroma_client = chromadb.PersistentClient(path=cfg.DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )
        self.top_k = top_k

    def retrieve(self, query, file_name, top_k=None):
        if top_k is None:
            top_k = self.top_k

        try:
            embedding_model, device = load_embedding_model()
            query_embedding = np.array(
                embedding_model.embed_query(query), dtype=np.float32
            )
            free_embedding_model(embedding_model, device)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"source": str(file_name)},
                include=["documents", "metadatas", "distances"],
            )

            documents = results.get("documents", [])
            if documents is None or len(documents) == 0:
                logger.info(
                    f"No documents found for file '{file_name}' and query '{query}'"
                )
                return []

            flattened_docs = documents[0] if documents else []
            return flattened_docs

        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return []


if __name__ == "__main__":
    import json
    import sys

    try:
        if len(sys.argv) < 3:
            print(
                "Usage: python retriever.py <filename> <question> [top_k]",
                file=sys.stderr,
            )
            sys.exit(1)
        filename = sys.argv[1]
        question = sys.argv[2]
        top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5

        retriever = Retriever(top_k=top_k)
        results = retriever.retrieve(question, filename)
        print(json.dumps(results))

    except Exception as e:
        logger.error(f"Error in command line arguments: {e}")
        sys.exit(1)
