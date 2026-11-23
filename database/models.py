from datetime import datetime, timezone
from database.db import db


def _now():
    return datetime.now(timezone.utc)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=_now)
    candidates = db.relationship("Candidate", backref="job", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description,
                "analysis": self.analysis, "candidate_count": len(self.candidates),
                "created_at": self.created_at.isoformat()}


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    filename = db.Column(db.String(300))
    skills = db.Column(db.JSON, default=list)
    education_text = db.Column(db.Text, default="")
    experience_text = db.Column(db.Text, default="")
    projects_text = db.Column(db.Text, default="")
    certifications_text = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="NEW")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=_now)
    result = db.relationship("ScreeningResult", uselist=False, backref="candidate",
                             cascade="all, delete-orphan")

    def to_dict(self):
        r = self.result
        return {
            "id": self.id, "job_id": self.job_id, "name": self.name, "email": self.email,
            "phone": self.phone, "skills": self.skills,
            "education_text": self.education_text, "experience_text": self.experience_text,
            "projects_text": self.projects_text, "certifications_text": self.certifications_text,
            "status": self.status, "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "score": {
                "overall": r.overall, "breakdown": r.breakdown,
                "matched_skills": r.matched_skills, "missing_skills": r.missing_skills,
                "experience_years": r.experience_years, "explanation": r.explanation,
            } if r else None,
        }


class ScreeningResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    overall = db.Column(db.Float)
    breakdown = db.Column(db.JSON)
    matched_skills = db.Column(db.JSON)
    missing_skills = db.Column(db.JSON)
    experience_years = db.Column(db.Float)
    explanation = db.Column(db.JSON)