import json
import os
import sys
from collections import defaultdict
from typing import List

import chromadb
import numpy as np
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from unstructured.partition.pdf import partition_pdf

from src.config import cfg
from src.logger import logger
from src.util import free_embedding_model, load_embedding_model


class PDFProcessor:
    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(path=cfg.DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )

    def _group_texts_by_page(self, elements):
        grouped = defaultdict(list)
        for element in elements:
            if hasattr(element, "text") and element.text and element.text.strip():
                page = (
                    getattr(element.metadata, "page_number", 0)
                    if hasattr(element, "metadata")
                    else 0
                )
                grouped[page].append(element.text)
        return [
            Document(page_content="\n".join(texts), metadata={"page_number": page})
            for page, texts in grouped.items()
        ]

    def process_pdf(self, file_name: str) -> bool:
        self.file_name = file_name
        logger.info(f"Processing PDF file: {self.file_name}")
        if not self.file_name.endswith(".pdf"):
            logger.error(f"File {self.file_name} is not a PDF.")
            return False
        if self._check_existing_embeddings():
            return True
        docs = self._process_pdf()
        if not docs:
            return False
        split_docs = self._run_splitter(docs)
        if not split_docs:
            return False
        embeddings = self._embed_docs(split_docs)
        if embeddings is None or len(embeddings) == 0:
            return False
        self._store_embeddings(split_docs, embeddings)
        logger.info(
            f"Successfully processed and stored embeddings for {self.file_name}."
        )
        return True

    def _process_pdf(self) -> list[Document] | None:
        file_path = os.path.join(cfg.DATA_DIR, self.file_name)

        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return None

        try:
            elements = partition_pdf(
                filename=file_path, strategy="auto", infer_table_structure=True
            )

            docs = self._group_texts_by_page(elements)

            if not docs:
                logger.info(f"No text found in PDF {self.file_name}.")
                return None
            logger.info(f"Extracted {len(docs)} page documents from {self.file_name}.")
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
                f"Split {len(docs)} page documents into {len(split_docs)} chunks for {self.file_name}."
            )
            return split_docs

        except Exception as e:
            logger.error(f"Error processing PDF {self.file_name} with splitter: {e}")
            return None

    def _embed_docs(self, docs: List[Document]) -> np.ndarray | None:
        try:
            logger.info(f"Embedding {len(docs)} documents for {self.file_name}.")
            embedding_model, device = load_embedding_model()
            all_embeddings = []

            for i, doc in enumerate(docs):
                try:
                    text = [doc.page_content]
                    embedding = embedding_model.embed_documents(text)
                    all_embeddings.extend(embedding)

                    if device == "cuda":
                        import torch

                        torch.cuda.empty_cache()

                except Exception as e:
                    logger.error(f"Error embedding document {i}: {e}")
                    continue
            embeddings = np.array(all_embeddings, dtype=np.float32)
            free_embedding_model(embedding_model, device)
            logger.info(f"Generated embeddings for {len(all_embeddings)} chunks.")
            return embeddings if len(all_embeddings) > 0 else None
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
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

    def format_response_to_text(
        success: bool, message: str = "", error: str = ""
    ) -> str:
        try:
            if success:
                content = f"SUCCESS\n{message}"
            else:
                content = f"ERROR\n{error}"

            return f"{cfg.RESPONSE_START}{content}{cfg.RESPONSE_END}"

        except Exception as e:
            return f"{cfg.RESPONSE_START}ERROR\n{str(e)}{cfg.RESPONSE_END}"

    if len(sys.argv) != 3:
        result = format_response_to_text(
            False, error="Usage: python pdf_processor.py <file_name> <output_file>"
        )
        print(result)
        sys.exit(1)

    file_name = sys.argv[1]
    output_file = sys.argv[2]

    try:
        processor = PDFProcessor()
        success = processor.process_pdf(file_name)

        if success:
            result_text = format_response_to_text(
                True, f"PDF {file_name} processed successfully"
            )
        else:
            result_text = format_response_to_text(
                False, error=f"Failed to process PDF {file_name}"
            )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_text)

    except Exception as e:
        error_result = format_response_to_text(False, error=str(e))
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(error_result)
        except:

            print(error_result)
        sys.exit(1)
