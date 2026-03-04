import numpy as np
from Backened.app.embeddings.embedding_model import EmbeddingModel


def test_embedding_output_shape():
    model = EmbeddingModel()
    text = "Machine learning engineer"

    embedding = model.encode(text)

    assert isinstance(embedding, np.ndarray)
    assert embedding.ndim == 1
    assert len(embedding) > 0


def test_embedding_is_normalized():
    model = EmbeddingModel()
    text = "Natural language processing"

    embedding = model.encode(text)

    norm = np.linalg.norm(embedding)

    # Since we normalized, norm should be ~1
    assert np.isclose(norm, 1.0, atol=1e-3)


def test_same_input_same_embedding():
    model = EmbeddingModel()
    text = "Deep learning with PyTorch"

    emb1 = model.encode(text)
    emb2 = model.encode(text)

    assert np.allclose(emb1, emb2, atol=1e-5)
    
def test_similar_texts_higher_similarity():
    model = EmbeddingModel()

    emb1 = model.encode("Machine learning engineer")
    emb2 = model.encode("ML engineer")
    emb3 = model.encode("Cooking recipes")

    from Backened.app.embeddings.similarity import cosine_similarity

    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)

    assert sim_related > sim_unrelated