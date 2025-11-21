from flask import Flask, render_template, request
from model import ResumeMatcher
from PyPDF2 import PdfReader
import docx
import re

app = Flask(__name__, static_folder="static", template_folder="templates")
matcher = ResumeMatcher()


# ------------------ CGPA EXTRACTION ------------------
def extract_cgpa(text):
    text = text.lower()

    # CASE 1 : "CGPA 7.6", "CGPA: 8.2", "cgpa - 9.1"
    m = re.search(r'cgpa[^0-9]*([0-9]\.?[0-9]?)', text)
    if m:
        try:
            cg = float(m.group(1))
            if cg <= 4:    # convert 4.0 scale to 10 scale
                cg = round(cg * 2.5, 2)
            return cg
        except:
            pass

    # CASE 2 : "3.5 / 4.0" → convert to 10 scale
    m2 = re.search(r'([0-9]\.?[0-9]?)\s*/\s*([0-9]\.?[0-9]?)', text)
    if m2:
        try:
            num = float(m2.group(1))
            den = float(m2.group(2))
            cg = round((num / den) * 10, 2)
            return cg
        except:
            pass

    return None


# ------------------ PDF / DOCX extractors ------------------
def extract_from_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

def extract_from_docx(path):
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


# ------------------ MAIN ROUTE ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    score = None
    cgpa = None
    message = ""
    shortlisted = False

    if request.method == "POST":
        jd = request.form["job_desc"]
        file = request.files["resume"]

        ext = file.filename.split(".")[-1].lower()
        path = f"temp.{ext}"
        file.save(path)

        # extract resume text
        resume_text = extract_from_pdf(path) if ext == "pdf" else extract_from_docx(path)

        # extract CGPA
        cgpa = extract_cgpa(resume_text)

        if cgpa is None:
            message = "❌ CGPA not found in resume."
            shortlisted = False

        elif cgpa < 6.5:
            message = f"❌ Rejected: CGPA {cgpa} is below 6.5"
            shortlisted = False

        else:
            # If CGPA OK → run AI score
            score = matcher.calculate_score(resume_text, jd)
            shortlisted = True
            message = f"✅ Shortlisted (CGPA: {cgpa})"

    return render_template("index.html",
                           result=score,
                           cgpa=cgpa,
                           shortlisted=shortlisted,
                           message=message)


if __name__ == "__main__":
    app.run(debug=True)
