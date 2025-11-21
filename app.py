from flask import Flask, render_template, request
from model import ResumeMatcher
from PyPDF2 import PdfReader
import docx, re

app = Flask(__name__, static_folder="static", template_folder="templates")
matcher = ResumeMatcher()

history = []   # stores shortlist history


# ------------------ CGPA Extraction ------------------
def extract_cgpa(text):
    t = text.lower()

    m = re.search(r'cgpa[^0-9]*([0-9]\.?[0-9]?)', t)
    if m:
        cg = float(m.group(1))
        if cg <= 4:
            cg *= 2.5
        return round(cg, 2)

    m2 = re.search(r'([0-9]\.?[0-9]?)\s*/\s*([0-9]\.?[0-9]?)', t)
    if m2:
        return round((float(m2.group(1)) / float(m2.group(2))) * 10, 2)

    return None


# ------------------ Experience ------------------
def extract_experience(text):
    matches = re.findall(r'([0-9]+)\s+years', text.lower())
    if matches:
        return max(int(x) for x in matches)
    return 0


# ------------------ Skill Extraction ------------------
skill_list = ["python", "java", "c++", "html", "css", "javascript",
              "machine learning", "deep learning", "sql", "excel",
              "communication", "react"]

def extract_skills(text):
    found = []
    t = text.lower()
    for s in skill_list:
        if s in t:
            found.append(s)
    return ", ".join(found) if found else "None"


# ------------------ PDF / DOCX extract ------------------
def extract_from_pdf(path):
    text = ""
    reader = PdfReader(path)
    for pg in reader.pages:
        t = pg.extract_text()
        if t:
            text += t + "\n"
    return text

def extract_from_docx(path):
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


# ------------------ MAIN ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    score = None
    cgpa = None
    skills = None
    exp = None
    preview = None
    message = ""

    if request.method == "POST":
        jd = request.form["job_desc"]
        file = request.files["resume"]

        ext = file.filename.split(".")[-1]
        path = f"temp.{ext}"
        file.save(path)

        # Extract resume text
        resume_text = extract_from_pdf(path) if ext == "pdf" else extract_from_docx(path)
        preview = resume_text[:1500]  # first 1500 chars

        # Extract data
        cgpa = extract_cgpa(resume_text)
        exp = extract_experience(resume_text)
        skills = extract_skills(resume_text)

        # Shortlist Logic
        if cgpa is None:
            message = "❌ CGPA not found."
            status = "Rejected"

        elif cgpa < 6.5:
            message = f"❌ CGPA {cgpa} < 6.5"
            status = "Rejected"

        else:
            score = matcher.calculate_score(resume_text, jd)
            message = "✅ Shortlisted!"
            status = "Shortlisted"

        # Save to history
        history.append({
            "cgpa": cgpa,
            "exp": exp,
            "score": score,
            "status": status
        })

    return render_template("index.html",
                           result=score,
                           cgpa=cgpa,
                           skills=skills,
                           exp=exp,
                           preview=preview,
                           message=message,
                           history=history)


if __name__ == "__main__":
    app.run(debug=True)

