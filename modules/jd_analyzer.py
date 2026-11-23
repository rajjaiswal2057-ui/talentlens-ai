"""Analyzes a Job Description: required/preferred skills, experience, education."""
import re
from modules.extractor import extract_skills

PREFERRED_MARKERS = ("preferred", "nice to have", "good to have", "bonus", "plus")
EDU_KEYWORDS = ["phd", "master", "m.tech", "mba", "bachelor", "b.tech", "b.e", "bsc", "diploma"]
CERT_KEYWORDS = ["certified", "certification", "certificate"]


def analyze_jd(jd_text: str) -> dict:
    required, preferred = set(), set()
    for line in jd_text.split("\n"):
        skills = extract_skills(line)
        if any(m in line.lower() for m in PREFERRED_MARKERS):
            preferred.update(skills)
        else:
            required.update(skills)
    preferred -= required

    exp = re.search(r"(\d+)\+?\s*(?:years|yrs|year)", jd_text.lower())
    text_lower = jd_text.lower()

    return {
        "required_skills": sorted(required),
        "preferred_skills": sorted(preferred),
        "min_experience_years": int(exp.group(1)) if exp else 0,
        "education": [e for e in EDU_KEYWORDS if e in text_lower],
        "certifications_required": any(c in text_lower for c in CERT_KEYWORDS),
    }