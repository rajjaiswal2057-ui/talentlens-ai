"""Runs one resume through parse -> extract -> score."""
from modules.parser import parse_resume
from modules.extractor import extract_resume_data
from modules.scorer import score_candidate


def process_resume(path: str, jd_analysis: dict, jd_text: str):
    resume = extract_resume_data(parse_resume(path))
    return resume, score_candidate(resume, jd_analysis, jd_text)