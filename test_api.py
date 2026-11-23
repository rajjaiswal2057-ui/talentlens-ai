import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from pathlib import Path
from app import create_app

app = create_app()
client = app.test_client()

JD = """We are hiring a Data Scientist.
Required: Python, SQL, Machine Learning, Pandas, Docker
2+ years experience. Bachelor's degree in Computer Science.
Preferred: AWS, NLP"""

job = client.post("/api/jobs", json={"title": "Data Scientist", "description": JD}).get_json()
paths = sorted(Path("data/sample_resumes").glob("*.docx"))
handles = [(open(p, "rb"), p.name) for p in paths]
res = client.post(f"/api/jobs/{job['id']}/upload", data={"files": handles},
                  content_type="multipart/form-data")
for h, _ in handles:
    h.close()
print("UPLOAD:", res.get_json(), "\n")

for c in client.get(f"/api/jobs/{job['id']}/candidates").get_json():
    print(c["rank"], c["name"], c["score"]["overall"], c["label"])

top = client.get(f"/api/jobs/{job['id']}/candidates").get_json()[0]
client.patch(f"/api/candidates/{top['id']}", json={"status": "SHORTLISTED"})
print("\nSTATS:", client.get("/api/stats").get_json())
print("\nCSV:\n", client.get(f"/api/jobs/{job['id']}/export.csv").get_data(as_text=True))