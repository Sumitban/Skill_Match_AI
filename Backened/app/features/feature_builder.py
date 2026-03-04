import numpy as np
import re
from Backened.app.embeddings.similarity import cosine_similarity


class FeatureBuilder:

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    # ----------------------------
    # Safe Embedding Helper
    # ----------------------------
    def _safe_encode(self, text):

        if not text or not text.strip():
            return None

        return self.embedding_model.encode(text)

    # ----------------------------
    # Similarity Features
    # ----------------------------
    def compute_similarity_features(self, resume, github, jd_embedding):

        resume_embedding = self._safe_encode(
            resume.get("raw_text", "")
        )

        skills_embedding = self._safe_encode(
            resume.get("skills_text", "")
        )

        github_embedding = self._safe_encode(
            github.get("readme_text", "")
        )

        resume_sim = cosine_similarity(resume_embedding, jd_embedding) if resume_embedding is not None else 0.0
        skills_sim = cosine_similarity(skills_embedding, jd_embedding) if skills_embedding is not None else 0.0
        github_sim = cosine_similarity(github_embedding, jd_embedding) if github_embedding is not None else 0.0

        return resume_sim, skills_sim, github_sim

    # ----------------------------
    # Numeric Features
    # ----------------------------
    def compute_numeric_features(self, resume, github, jd_text):

        years_experience = float(resume.get("years_experience", 0))

        resume_skills = set(
            skill.lower() for skill in resume.get("skills", [])
        )

        jd_words = set(
            re.findall(r"\b\w+\b", jd_text.lower())
        )

        skill_overlap = len([
            skill for skill in resume_skills
            if skill in jd_words
        ])

        repo_count = float(github.get("repo_count", 0) or 0)
        star_count = float(github.get("total_stars", 0) or 0)
        fork_ratio = float(github.get("fork_ratio", 0.0) or 0.0)

        language_distribution = github.get("language_distribution", {})

        language_match_score = sum(
            1 for lang in language_distribution
            if lang.lower() in jd_text.lower()
        )

        return (
            years_experience,
            skill_overlap,
            repo_count,
            star_count,
            fork_ratio,
            language_match_score
        )

    # ----------------------------
    # Final Feature Vector
    # ----------------------------
    def build_feature_vector(self, resume, github, jd_embedding, jd_text):

        sim_features = self.compute_similarity_features(
            resume,
            github,
            jd_embedding
        )

        numeric_features = self.compute_numeric_features(
            resume,
            github,
            jd_text
        )

        feature_vector = np.array(
            sim_features + numeric_features,
            dtype=float
        )

        return feature_vector