import re

KNOWN_SECTION_KEYWORDS = {
    "skills": ["skills", "technical skills", "core competencies"],
    "experience": ["experience", "work experience", "employment history"],
    "education": ["education", "academic background"],
    "projects": ["projects", "personal projects"]
}

# Precompute flat keyword list once
FLAT_KEYWORDS = [kw.lower() for values in KNOWN_SECTION_KEYWORDS.values() for kw in values]


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def is_header_candidate(lines, index):
    line = lines[index].strip()

    if not line:
        return False

    word_count = len(line.split())
    if word_count > 6:
        return False

    if line.endswith("."):
        return False

    line_lower = line.lower()

    # Strong signal: exact keyword match
    if line_lower in FLAT_KEYWORDS:
        return True

    # Medium signal: contains keyword but short
    if any(kw in line_lower for kw in FLAT_KEYWORDS):
        if word_count <= 4:
            return True

    # Structural signal: surrounded by blank lines
    prev_blank = index > 0 and not lines[index - 1].strip()
    next_blank = index < len(lines) - 1 and not lines[index + 1].strip()

    uppercase_ratio = sum(1 for c in line if c.isupper()) / max(len(line), 1)

    if (prev_blank or next_blank) and (uppercase_ratio > 0.5):
        return True

    return False


def normalize_header(header_line):
    header_line = header_line.lower()
    for section, keywords in KNOWN_SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in header_line:
                return section
    return None


def extract_sections(text):
    text = normalize_text(text)
    lines = text.split("\n")

    headers = []

    for i in range(len(lines)):
        if is_header_candidate(lines, i):
            normalized = normalize_header(lines[i])
            if normalized:
                headers.append((normalized, i))

    # Remove duplicate consecutive headers
    unique_headers = []
    seen_positions = set()

    for section, idx in headers:
        if idx not in seen_positions:
            unique_headers.append((section, idx))
            seen_positions.add(idx)

    sections = {}

    for i, (section_name, start_idx) in enumerate(unique_headers):
        end_idx = unique_headers[i + 1][1] if i + 1 < len(unique_headers) else len(lines)
        content = "\n".join(lines[start_idx + 1:end_idx]).strip()

        if section_name in sections:
            sections[section_name] += "\n" + content
        else:
            sections[section_name] = content

    # Fallback if nothing detected
    if not sections:
        sections["full_text"] = text

    return sections