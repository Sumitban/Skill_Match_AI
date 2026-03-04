
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
import numpy as np


class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> np.ndarray:
        embedding = self.model.encode(text)
        return normalize([embedding])[0]