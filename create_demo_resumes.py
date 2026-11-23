import docx

CANDIDATES = {
    "candidate_B_ml.docx": ("Aarav Mehta", "aarav.mehta@example.com", "+91-9811111111",
        "Python, SQL, Machine Learning, Deep Learning, Pandas, Scikit-learn, NLP, Docker",
        "M.Tech in Data Science, IIT Demo Institute, 2021-2023",
        ["ML Engineer, Insight Labs, 2023 - Present",
         "Built NLP models for resume classification using Python and Scikit-learn."],
        "Google Data Analytics Certificate"),
    "candidate_C_frontend.docx": ("Diya Patel", "diya.patel@example.com", "+91-9822222222",
        "JavaScript, TypeScript, React, HTML, CSS, Git",
        "B.Tech in Information Technology, Demo University, 2018-2022",
        ["Frontend Developer, PixelWorks, 2022 - 2025",
         "Built responsive React dashboards for e-commerce clients."],
        ""),
    "candidate_D_analytics.docx": ("Kabir Singh", "kabir.singh@example.com", "+91-9833333333",
        "SQL, Excel, Python, Pandas, PostgreSQL",
        "B.Sc in Statistics, Demo College, 2019-2022",
        ["Data Analyst, MetricHub, 2022 - 2025",
         "Created SQL reports and Python analysis for sales teams."],
        "Microsoft Excel Expert Certification"),
    "candidate_E_backend.docx": ("Neha Iyer", "neha.iyer@example.com", "+91-9844444444",
        "Python, Flask, Docker, AWS, Kubernetes, PostgreSQL, Linux, Git",
        "B.E. in Computer Engineering, Demo Institute, 2017-2021",
        ["Backend Engineer, CloudNest, 2021 - 2025",
         "Designed Flask REST APIs deployed on AWS with Docker and Kubernetes."],
        "AWS Certified Solutions Architect"),
}

for filename, (name, email, phone, skills, edu, exp, cert) in CANDIDATES.items():
    d = docx.Document()
    d.add_heading(name, level=1)
    d.add_paragraph(f"Email: {email} | Phone: {phone}")
    d.add_heading("Skills", level=2)
    d.add_paragraph(skills)
    d.add_heading("Education", level=2)
    d.add_paragraph(edu)
    d.add_heading("Experience", level=2)
    for line in exp:
        d.add_paragraph(line)
    if cert:
        d.add_heading("Certifications", level=2)
        d.add_paragraph(cert)
    d.save(f"data/sample_resumes/{filename}")
    print("created", filename)