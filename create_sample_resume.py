import docx

doc = docx.Document()
doc.add_heading('Rahul Sharma', level=1)
doc.add_paragraph('Email: rahul.sharma@example.com | Phone: +91-9876543210')

doc.add_heading('Skills', level=2)
doc.add_paragraph('Python, SQL, Machine Learning, Pandas, Scikit-learn, NLP')

doc.add_heading('Education', level=2)
doc.add_paragraph('B.Tech in Computer Science, PDEU, 2022-2026')

doc.add_heading('Experience', level=2)
doc.add_paragraph('Data Analyst Intern, XYZ Corp, 2025 - Present')
doc.add_paragraph('Built ML models for customer churn prediction using Python and Scikit-learn.')

doc.add_heading('Certifications', level=2)
doc.add_paragraph('AWS Certified Cloud Practitioner')

doc.save('data/sample_resumes/sample_candidate_A.docx')
print("Sample resume created")
