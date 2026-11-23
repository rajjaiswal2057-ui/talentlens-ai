import csv
import io
import uuid
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.utils import secure_filename

from config import Config
from database.db import db
from database.models import Candidate, Job, ScreeningResult
from modules.jd_analyzer import analyze_jd
from modules.parser import ParsingError, is_allowed_file
from modules.pipeline import process_resume
from modules.ranker import rank_candidates

VALID_STATUSES = ["NEW", "REVIEW", "SHORTLISTED", "REJECTED"]


def ranked_candidates(job_id):
    rows = Candidate.query.filter_by(job_id=job_id).join(ScreeningResult).all()
    return rank_candidates([c.to_dict() for c in rows])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/screening")
    def screening_page():
        return render_template("screening.html")

    @app.route("/jobs/<int:job_id>/candidates")
    def candidates_page(job_id):
        return render_template("candidates.html", job_id=job_id)

    @app.route("/candidates/<int:cand_id>")
    def candidate_page(cand_id):
        return render_template("candidate_detail.html", cand_id=cand_id)

    @app.route("/health")
    def health():
        return {"status": "ok", "app": "TalentLens AI"}

    # ---------- Jobs ----------
    @app.post("/api/jobs")
    def create_job():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()
        if not title or len(description) < 30:
            return jsonify({"error": "Title and a job description (30+ chars) are required"}), 400
        job = Job(title=title, description=description, analysis=analyze_jd(description))
        db.session.add(job)
        db.session.commit()
        return jsonify(job.to_dict()), 201

    @app.get("/api/jobs")
    def list_jobs():
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        return jsonify([j.to_dict() for j in jobs])

    # ---------- Upload + screening ----------
    @app.post("/api/jobs/<int:job_id>/upload")
    def upload_resumes(job_id):
        job = db.get_or_404(Job, job_id)
        results = []
        for f in request.files.getlist("files"):
            name = secure_filename(f.filename or "")
            if not name or not is_allowed_file(name):
                results.append({"filename": f.filename, "status": "error",
                                "error": "Only PDF and DOCX files are supported"})
                continue
            saved = Config.UPLOAD_FOLDER / f"{uuid.uuid4().hex}_{name}"
            f.save(saved)
            try:
                resume, score = process_resume(str(saved), job.analysis, job.description)
            except ParsingError as e:
                saved.unlink(missing_ok=True)
                results.append({"filename": name, "status": "error", "error": str(e)})
                continue
            cand = Candidate(
                job_id=job.id, name=resume["name"] or Path(name).stem,
                email=resume["email"], phone=resume["phone"], filename=saved.name,
                skills=resume["skills"], education_text=resume["education_text"],
                experience_text=resume["experience_text"],
                projects_text=resume["projects_text"],
                certifications_text=resume["certifications_text"],
            )
            cand.result = ScreeningResult(
                overall=score["overall"], breakdown=score["breakdown"],
                matched_skills=score["matched_skills"], missing_skills=score["missing_skills"],
                experience_years=score["experience_years"], explanation=score["explanation"],
            )
            db.session.add(cand)
            db.session.commit()
            results.append({"filename": name, "status": "ok",
                            "candidate_id": cand.id, "score": score["overall"]})
        return jsonify(results)

    # ---------- Candidates ----------
    @app.get("/api/jobs/<int:job_id>/candidates")
    def list_candidates(job_id):
        db.get_or_404(Job, job_id)
        q = request.args.get("q", "").strip().lower()
        skill = request.args.get("skill", "").strip().lower()
        status = request.args.get("status", "").upper()
        min_score = request.args.get("min_score", 0, type=float)

        items = ranked_candidates(job_id)  # rank is computed before filtering
        out = []
        for c in items:
            if c["score"]["overall"] < min_score:
                continue
            if status and c["status"] != status:
                continue
            if q and q not in (c["name"] or "").lower() and q not in (c["email"] or "").lower():
                continue
            if skill and skill not in [s.lower() for s in c["skills"]]:
                continue
            out.append(c)
        return jsonify(out)

    @app.get("/api/candidates/<int:cand_id>")
    def get_candidate(cand_id):
        cand = db.get_or_404(Candidate, cand_id)
        ranked = ranked_candidates(cand.job_id)
        data = next(c for c in ranked if c["id"] == cand_id)
        data["job"] = {"id": cand.job.id, "title": cand.job.title, "analysis": cand.job.analysis}
        data["total_candidates"] = len(ranked)
        return jsonify(data)

    @app.patch("/api/candidates/<int:cand_id>")
    def update_candidate(cand_id):
        cand = db.get_or_404(Candidate, cand_id)
        data = request.get_json(silent=True) or {}
        if "status" in data:
            if data["status"] not in VALID_STATUSES:
                return jsonify({"error": f"Status must be one of {VALID_STATUSES}"}), 400
            cand.status = data["status"]
        if "notes" in data:
            cand.notes = str(data["notes"])[:2000]
        db.session.commit()
        return jsonify({"id": cand.id, "status": cand.status, "notes": cand.notes})

    # ---------- Export + stats ----------
    @app.get("/api/jobs/<int:job_id>/export.csv")
    def export_csv(job_id):
        db.get_or_404(Job, job_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Rank", "Candidate", "Email", "Match Score", "Skills Match",
                         "Experience (yrs)", "Status"])
        for c in ranked_candidates(job_id):
            s = c["score"]
            writer.writerow([c["rank"], c["name"], c["email"], s["overall"],
                             s["breakdown"]["skills"], s["experience_years"], c["status"]])
        return Response(buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=job_{job_id}_ranking.csv"})

    @app.get("/api/stats")
    def stats():
        job_id = request.args.get("job_id", type=int)
        query = Candidate.query.join(ScreeningResult)
        if job_id:
            query = query.filter(Candidate.job_id == job_id)
        rows = query.all()
        scores = [c.result.overall for c in rows]
        status_counts = {s: 0 for s in VALID_STATUSES}
        for c in rows:
            status_counts[c.status] += 1
        buckets = {"0-39": 0, "40-59": 0, "60-79": 0, "80-100": 0}
        for s in scores:
            key = "0-39" if s < 40 else "40-59" if s < 60 else "60-79" if s < 80 else "80-100"
            buckets[key] += 1
        return jsonify({
            "resumes_screened": len(rows),
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "shortlisted": status_counts["SHORTLISTED"],
            "status_counts": status_counts,
            "score_distribution": buckets,
        })

    return app


if __name__ == "__main__":
    create_app().run(debug=True)