"""Semantic matching using Sentence Transformers + skill alias handling."""
from sentence_transformers import SentenceTransformer, util
from config import Config

_model = None

# Short forms that should count as the same skill.
SKILL_ALIASES = {
    "ml": "machine learning", "js": "javascript", "ts": "typescript",
    "sklearn": "scikit-learn", "nodejs": "node.js", "ai": "machine learning",
    "dl": "deep learning", "k8s": "kubernetes", "postgres": "postgresql",
}


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(Config.EMBEDDING_MODEL)
    return _model


def normalize_skill(skill: str) -> str:
    s = skill.lower().strip()
    return SKILL_ALIASES.get(s, s)


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between resume and JD embeddings, clipped to 0-1."""
    model = _get_model()
    emb = model.encode([resume_text, jd_text], convert_to_tensor=True)
    score = float(util.cos_sim(emb[0], emb[1]))
    return max(0.0, min(1.0, score))


def match_skills(required: list, candidate_skills: list, threshold: float = 0.8):
    """
    Returns (matched, missing). Alias-normalised exact match first,
    then embedding similarity as a fallback for near-synonyms.
    """
    cand = {normalize_skill(s) for s in candidate_skills}
    matched, missing = [], []
    model = _get_model()
    cand_list = list(cand)
    cand_emb = model.encode(cand_list, convert_to_tensor=True) if cand_list else None

    for req in required:
        r = normalize_skill(req)
        if r in cand:
            matched.append(req)
            continue
        if cand_emb is not None:
            sim = util.cos_sim(model.encode(r, convert_to_tensor=True), cand_emb).max().item()
            if sim >= threshold:
                matched.append(req)
                continue
        missing.append(req)
    return matched, missing