import numpy as np
from Backened.app.embeddings.similarity import cosine_similarity


def test_identical_vectors():
    vec = np.array([1.0, 0.0, 0.0])
    assert cosine_similarity(vec, vec) == 1.0


def test_orthogonal_vectors():
    vec1 = np.array([1.0, 0.0])
    vec2 = np.array([0.0, 1.0])
    assert cosine_similarity(vec1, vec2) == 0.0


def test_opposite_vectors():
    vec1 = np.array([1.0, 0.0])
    vec2 = np.array([-1.0, 0.0])
    assert cosine_similarity(vec1, vec2) == -1.0