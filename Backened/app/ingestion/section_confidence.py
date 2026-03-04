

def compute_section_confidence(sections):
    score = 0

    if "skills" in sections and len(sections["skills"]) > 30:
        score += 1

    if "experience" in sections and len(sections["experience"]) > 100:
        score += 1

    if "education" in sections and len(sections["education"]) > 20:
        score += 1

    return score / 3.0 

def is_confident(confidence_score, threshold=0.6):
    return confidence_score >= threshold