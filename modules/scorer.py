"""Transparent weighted scoring + explanation generation."""
import re
from datetime import datetime
from config import Config
from modules.matcher import semantic_similarity, match_skills

DEGREE_LEVELS = [("phd", 1.0), ("master", 0.9), ("m.tech", 0.9), ("mba", 0.9),
                 ("bachelor", 0.8), ("b.tech", 0.8), ("b.e", 0.8), ("bsc", 0.8), ("diploma", 0.5)]


def estimate_experience_years(experience_text: str) -> float:
    """Sum year ranges like '2023 - 2025' or '2025 - Present'."""
    total, now = 0.0, datetime.now().year
    for start, end in re.findall(r"(\d{4})\s*[-–to]+\s*(\d{4}|present)", experience_text.lower()):
        end_year = now if end == "present" else int(end)
        total += max(0, end_year - int(start))
    explicit = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", experience_text.lower())
    if explicit:
        total = max(total, max(float(x) for x in explicit))
    return round(total, 1)


def education_score(education_text: str, jd_education: list) -> float:
    if not jd_education:
        return 1.0
    text = education_text.lower()
    for keyword, score in DEGREE_LEVELS:
        if keyword in text:
            return score
    return 0.3


def score_candidate(resume: dict, jd: dict, jd_text: str) -> dict:
    w = Config.SCORE_WEIGHTS
    semantic = semantic_similarity(resume["raw_text"], jd_text)

    matched, missing = match_skills(jd["required_skills"], resume["skills"])
    skills_score = len(matched) / len(jd["required_skills"]) if jd["required_skills"] else 1.0
    pref_matched, pref_missing = match_skills(jd["preferred_skills"], resume["skills"])

    years = estimate_experience_years(resume["experience_text"])
    need = jd["min_experience_years"]
    exp_score = min(1.0, years / need) if need else (1.0 if years > 0 else 0.5)

    edu_score = education_score(resume["education_text"], jd["education"])
    has_certs = bool(resume["certifications_text"].strip())
    cert_score = 1.0 if has_certs else (0.0 if jd["certifications_required"] else 0.5)

    overall = (w["semantic_match"] * semantic + w["required_skills"] * skills_score +
               w["experience"] * exp_score + w["education"] * edu_score +
               w["certifications"] * cert_score)

    explanation = []
    if semantic >= 0.5:
        explanation.append(f"✓ Strong semantic alignment with the job description ({semantic:.0%})")
    else:
        explanation.append(f"⚠ Limited semantic alignment with the job description ({semantic:.0%})")
    if jd["required_skills"]:
        explanation.append(f"✓ {len(matched)} of {len(jd['required_skills'])} required skills detected")
    if missing:
        explanation.append(f"⚠ Missing required skills: {', '.join(missing)}")
    if pref_missing:
        explanation.append(f"⚠ Preferred skills not detected: {', '.join(pref_missing)}")
    if need:
        tag = "✓" if years >= need else "⚠"
        explanation.append(f"{tag} Estimated experience {years} yrs vs {need}+ required")

    return {
        "overall": round(overall * 100, 1),
        "breakdown": {"semantic": round(semantic * 100, 1), "skills": round(skills_score * 100, 1),
                      "experience": round(exp_score * 100, 1), "education": round(edu_score * 100, 1),
                      "certifications": round(cert_score * 100, 1)},
        "matched_skills": matched, "missing_skills": missing,
        "preferred_matched": pref_matched, "preferred_missing": pref_missing,
        "experience_years": years, "explanation": explanation,
    }