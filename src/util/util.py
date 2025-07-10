import torch
from langchain_huggingface import HuggingFaceEmbeddings

from config import cfg


def load_embedding_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embedding_model = HuggingFaceEmbeddings(
        model_name=cfg.EMBEDDING_MODEL_NAME,
        model_kwargs={
            **cfg.EMBEDDING_MODEL_KWARGS,
            "device": device,
        },
        encode_kwargs=cfg.ENCODE_KWARGS,
    )
    return embedding_model, device


def free_embedding_model(embedding_model, device):
    del embedding_model
    import gc

    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
