from flask import Flask, render_template, request
from model import ResumeMatcher
from PyPDF2 import PdfReader
import docx

app = Flask(__name__, static_folder="static", template_folder="templates")
matcher = ResumeMatcher()

def extract_from_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        t = page.extract_text()
        if t: text += t + "\n"
    return text

def extract_from_docx(path):
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)

@app.route("/", methods=["GET", "POST"])
def home():
    score = None
    if request.method == "POST":
        jd = request.form["job_desc"]
        file = request.files["resume"]
        ext = file.filename.split(".")[-1]
        path = f"temp.{ext}"
        file.save(path)
        if ext == "pdf":
            resume_text = extract_from_pdf(path)
        else:
            resume_text = extract_from_docx(path)
        score = matcher.calculate_score(resume_text, jd)
    return render_template("index.html", result=score)

if __name__ == "__main__":
    app.run(debug=True)
