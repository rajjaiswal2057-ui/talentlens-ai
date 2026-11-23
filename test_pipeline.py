from modules.parser import parse_resume
from modules.extractor import extract_resume_data
from modules.jd_analyzer import analyze_jd
from modules.scorer import score_candidate
from modules.ranker import rank_candidates

JD = """We need a Data Scientist.
Required: Python, SQL, Machine Learning, Pandas, Docker
2+ years experience. Bachelor's degree in Computer Science.
Preferred: AWS, NLP"""

jd = analyze_jd(JD)
print("JD analysis:", jd)

resume = extract_resume_data(parse_resume("data/sample_resumes/sample_candidate_A.docx"))
result = {"name": resume["name"], "score": score_candidate(resume, jd, JD)}

for c in rank_candidates([result]):
    print(c["rank"], c["name"], c["score"]["overall"], c["label"])
    print(c["score"]["breakdown"])
    print("\n".join(c["score"]["explanation"]))