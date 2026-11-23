"""
TalentLens AI - Information Extractor
Extracts structured fields (name, contact info, skills, education,
experience, certifications) from raw resume text.
"""

import re
import spacy

# Load the spaCy model once at import time — loading it per-call is slow.
_nlp = spacy.load("en_core_web_sm")

# Expandable skills database, grouped by category.
SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "c++", "javascript", "typescript", "c#", "go", "rust", "c"
    ],
    "Web": [
        "html", "css", "react", "angular", "vue", "node.js", "nodejs", "express", "flask", "django"
    ],
    "Data": [
        "sql", "mysql", "postgresql", "mongodb", "pandas", "numpy", "excel"
    ],
    "AI/ML": [
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
        "scikit-learn", "sklearn", "computer vision", "ml", "ai"
    ],
    "Cloud/DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "ci/cd", "linux"
    ],
}

# Flatten to a single lookup list, longest-first so multi-word skills
# (e.g. "machine learning") match before their substrings do.
ALL_SKILLS = sorted(
    {skill for group in SKILLS_DB.values() for skill in group},
    key=len,
    reverse=True,
)

SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "core competencies"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}

# Words that look like a header line, so they are never mistaken for a name.
_HEADER_WORDS = {h for hs in SECTION_HEADERS.values() for h in hs} | {"resume", "curriculum vitae", "cv"}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[\s-]?)?\d{10}|\+?\d{1,3}[\s-]?\d{3,5}[\s-]?\d{3,5}")


def extract_email(text: str) -> str | None:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_REGEX.search(text)
    return match.group(0).strip() if match else None


def extract_name(text: str) -> str | None:
    """
    Name is usually the first clean line of a resume (2-4 alphabetic words).
    If that fails, fall back to spaCy PERSON detection, run line by line so
    an entity can never spill across a newline.
    """
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()][:6]

    for line in lines:
        if "@" in line or any(ch.isdigit() for ch in line) or line.lower().rstrip(":") in _HEADER_WORDS:
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w.replace(".", "").replace("-", "").isalpha() for w in words):
            return line.title() if line.isupper() else line

    for line in lines:
        for ent in _nlp(line).ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
    return None


def split_into_sections(text: str) -> dict:
    """
    Split resume text into sections based on common headers.
    Returns a dict like {"skills": "...", "education": "...", ...}.
    """
    lines = text.split("\n")
    sections = {"header": []}
    current_section = "header"

    header_lookup = {}
    for section_name, headers in SECTION_HEADERS.items():
        for h in headers:
            header_lookup[h] = section_name

    for line in lines:
        clean_line = line.strip().lower().rstrip(":")
        if clean_line in header_lookup:
            current_section = header_lookup[clean_line]
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line)

    return {name: "\n".join(content).strip() for name, content in sections.items()}


def extract_skills(text: str) -> list:
    """
    Find known skills mentioned anywhere in the resume text.
    Case-insensitive, whole-word matching to avoid false positives.
    """
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_resume_data(text: str) -> dict:
    """
    Run full extraction on a resume's raw text and return a structured dict.
    """
    sections = split_into_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education_text": sections.get("education", ""),
        "experience_text": sections.get("experience", ""),
        "projects_text": sections.get("projects", ""),
        "certifications_text": sections.get("certifications", ""),
        "raw_text": text,
    }