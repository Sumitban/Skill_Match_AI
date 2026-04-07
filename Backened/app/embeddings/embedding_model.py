
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from Backened.app.config import load_config
import numpy as np

_shared_model = None

class EmbeddingModel:
    
    def __init__(self):
        global _shared_model
        
        if _shared_model is None:
            config = load_config()
            model_name = config["Embedding"]["MODEL_NAME"]
            _shared_model = SentenceTransformer(model_name)
            
        self.model = _shared_model

    def encode(self, text: str) -> np.ndarray:
        embedding = self.model.encode(text)
        return normalize([embedding])[0]