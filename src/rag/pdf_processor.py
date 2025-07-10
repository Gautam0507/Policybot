import os
from typing import List

import chromadb
import numpy as np
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from unstructured.partition.pdf import partition_pdf

from logger import logger
from src.config import cfg
from src.util import free_embedding_model, load_embedding_model


class PDFProcessor:
    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(path=cfg.DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )

    def process_pdf(self, file_name: str) -> None:
        self.file_name = file_name
        logger.info(f"Processing PDF file: {self.file_name}")
        if not self.file_name.endswith(".pdf"):
            logger.error(f"File {self.file_name} is not a PDF.")
            return
        if self._check_existing_embeddings():
            return
        docs = self._process_pdf()
        if not docs:
            return
        split_docs = self._run_splitter(docs)
        if not split_docs:
            return
        embeddings = self._embed_docs(split_docs)
        if not embeddings:
            return
        self._store_embeddings(split_docs, embeddings)
        logger.info(
            f"Successfully processed and stored embeddings for {self.file_name}."
        )

    def _process_pdf(self) -> list[Document] | None:
        file_path = os.path.join(cfg.DATA_DIR, self.file_name)
        try:
            elements = partition_pdf(filename=file_path, strategy="fast")
            texts = [
                element.text
                for element in elements
                if hasattr(element, "text") and element.text.strip()
            ]
            docs = [Document(page_content=text) for text in texts]
            if not texts:
                logger.info(f"No text found in PDF {self.file_name}.")
                return None
            logger.info(f"Extracted {len(docs)} documents from {self.file_name}.")
            return docs

        except Exception as e:
            logger.error(f"Error processing PDF {self.file_name}: {e}")
            return None

    def _check_existing_embeddings(self) -> bool:
        existing_docs = self.collection.get(where={"source": self.file_name}, limit=1)
        if existing_docs and existing_docs.get("ids"):
            logger.info(
                f"Document embeddings already exist in the collection for {self.file_name}."
            )
            return True
        logger.info(
            f"No existing embeddings found in the collection for {self.file_name}."
        )
        return False

    def _run_splitter(self, docs: List[Document]) -> List[Document] | None:
        try:
            embedding_model, device = load_embedding_model()
            splitter = SemanticChunker(
                embeddings=embedding_model,
                breakpoint_threshold_type=cfg.BREAKPOINT_THRESHOLD_TYPE,
                breakpoint_threshold_amount=cfg.BREAKPOINT_THRESHOLD_AMOUNT,
            )
            split_docs = splitter.split_documents(docs)
            free_embedding_model(embedding_model, device)
            logger.info(
                f"Split {len(docs)} documents into {len(split_docs)} chunks for {self.file_name}."
            )
            return split_docs

        except Exception as e:
            logger.error(f"Error processing PDF {self.file_name} with splitter: {e}")
            return None

    def _embed_docs(self, docs: List[Document]) -> np.ndarray | None:
        try:
            embedding_model, device = load_embedding_model()
            texts = [doc.page_content for doc in docs]
            embeddings = np.array(
                embedding_model.embed_documents(texts), dtype=np.float32
            )
            free_embedding_model(embedding_model, device)
            logger.info(f"Embedding {len(docs)} documents for {self.file_name}.")
            return embeddings

        except Exception as e:
            logger.error(f"Error embedding documents for {self.file_name}: {e}")
            return None

    def _store_embeddings(self, docs: List[Document], embeddings: np.ndarray) -> None:
        try:
            ids = [f"{self.file_name}_{i}" for i in range(len(docs))]
            self.collection.add(
                ids=ids,
                documents=[doc.page_content for doc in docs],
                embeddings=embeddings.tolist(),
                metadatas=[{"source": self.file_name} for _ in range(len(docs))],
            )
            logger.info(f"Stored embeddings for {len(docs)} documents.")
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")


if __name__ == "__main__":
    pass
