from flask import Flask, render_template, request, redirect, session, url_for
from model import ResumeMatcher
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import docx, re, os, traceback, uuid

app = Flask(__name__, static_folder="static", template_folder="templates")

# Secret key for login sessions (consider moving to environment variable)
app.secret_key = "supersecret123"

matcher = ResumeMatcher()

# temporary shortlist history (in-memory)
history = []

# Allowed extensions and maximum upload size (~4.5 MB)
ALLOWED_EXT = {"pdf", "docx"}
MAX_UPLOAD_BYTES = 4_500_000


# ------------------ Utility & Extraction Helpers ------------------
def is_allowed_filename(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXT

def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""

def safe_save_file(file_storage, dest_path):
    """
    Save an uploaded file to dest_path.
    Returns True on success, raises on failure.
    """
    file_storage.save(dest_path)
    return True


# ------------------ CGPA Extraction ------------------
def extract_cgpa(text):
    if not text:
        return None
    t = text.lower()

    m = re.search(r'cgpa[^0-9]*([0-9]\.?[0-9]?)', t)
    if m:
        try:
            cg = float(m.group(1))
            if cg <= 4:
                cg *= 2.5
            return round(cg, 2)
        except:
            pass

    m2 = re.search(r'([0-9]\.?[0-9]?)\s*/\s*([0-9]\.?[0-9]?)', t)
    if m2:
        try:
            return round((float(m2.group(1)) / float(m2.group(2))) * 10, 2)
        except:
            pass

    return None


# ------------------ Experience Extraction ------------------
def extract_experience(text):
    if not text:
        return 0
    matches = re.findall(r'([0-9]+)\s+years', text.lower())
    if matches:
        return max(int(x) for x in matches)
    return 0


# ------------------ Skill Extraction ------------------
skill_list = [
    "python", "java", "c++", "html", "css", "javascript",
    "machine learning", "deep learning", "sql", "excel",
    "communication", "react", "node", "flutter", "django"
]

def extract_skills(text):
    if not text:
        return "None"
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
        try:
            t = pg.extract_text()
        except Exception:
            t = ""
        if t:
            text += t + "\n"
    return text

def extract_from_docx(path):
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


# ------------------ LOGIN ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")

        # Simple hardcoded auth for now (change for production)
        if user == "admin" and pwd == "admin123":
            session["logged_in"] = True
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")


# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
def dashboard():
    if "logged_in" not in session:
        return redirect("/login")
    return render_template("dashboard.html", history=history)


# ------------------ MAIN PAGE ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    score = None
    cgpa = None
    skills = None          # skills found in resume (string)
    exp = None
    preview = None
    message = ""
    status = None

    # helper: extract required skills from job description using skill_list
    def extract_required_skills_from_jd(jd_text):
        if not jd_text:
            return []
        t = jd_text.lower()
        required = []
        for s in skill_list:
            # match whole word or phrase
            if s in t:
                required.append(s)
        return required

    if request.method == "POST":
        try:
            jd = request.form.get("job_desc", "") or ""
            file = request.files.get("resume")

            if not file or file.filename == "":
                message = "No file uploaded. Please choose a PDF or DOCX resume."
                status = "Rejected"
                return render_template("index.html", result=score, cgpa=cgpa, skills=skills,
                                       exp=exp, preview=preview, message=message, history=history)

            filename = secure_filename(file.filename)
            ext = get_extension(filename)
            if ext == "":
                message = "Uploaded file has no extension. Use .pdf or .docx."
                status = "Rejected"
                return render_template("index.html", result=score, cgpa=cgpa, skills=skills,
                                       exp=exp, preview=preview, message=message, history=history)

            if ext not in ALLOWED_EXT:
                message = f"Unsupported file type: .{ext}. Only PDF and DOCX are allowed."
                status = "Rejected"
                return render_template("index.html", result=score, cgpa=cgpa, skills=skills,
                                       exp=exp, preview=preview, message=message, history=history)

            # check size
            file_stream = file.stream
            file_stream.seek(0, os.SEEK_END)
            size = file_stream.tell()
            file_stream.seek(0)
            if size and size > MAX_UPLOAD_BYTES:
                message = f"File too large ({round(size/1e6,2)} MB). Max allowed ≈4.5 MB."
                status = "Rejected"
                return render_template("index.html", result=score, cgpa=cgpa, skills=skills,
                                       exp=exp, preview=preview, message=message, history=history)

            # save temp
            unique_name = f"upload_{uuid.uuid4().hex}.{ext}"
            temp_dir = "/tmp" if os.path.exists("/tmp") else "."
            temp_path = os.path.join(temp_dir, unique_name)
            safe_save_file(file, temp_path)

            # extract resume text
            resume_text = ""
            if ext == "pdf":
                resume_text = extract_from_pdf(temp_path)
            else:
                resume_text = extract_from_docx(temp_path)

            preview = (resume_text or "")[:2000]
            cgpa = extract_cgpa(resume_text)
            exp = extract_experience(resume_text)
            skills_found = extract_skills(resume_text)              # string like "python, react"
            skills = skills_found

            # extract required skills from JD
            required_skills = extract_required_skills_from_jd(jd)
            # normalize sets
            req_set = set([s.lower() for s in required_skills])
            found_set = set([s.strip().lower() for s in (skills_found or "").split(",") if s.strip()])

            # matched and missing skills
            matched_skills = sorted(list(found_set.intersection(req_set)))
            missing_skills = sorted(list(req_set.difference(found_set)))

            # skill match score: percent of required skills present (if no required skills, fallback to overall text score)
            if len(req_set) > 0:
                skill_score = round((len(matched_skills) / len(req_set)) * 100, 2)
            else:
                # no explicit skills in JD: use text similarity as fallback
                if jd.strip():
                    skill_score = matcher.calculate_score(resume_text, jd)
                else:
                    skill_score = None

            # overall similarity (existing lightweight model)
            overall_score = matcher.calculate_score(resume_text, jd) if jd.strip() else None
            score = overall_score  # keep backward-compatible variable

            # determine shortlist status (CGPA rule applies)
            if cgpa is None:
                cgpa_note = "missing"
                cgpa_status = "Missing"
                status = "Rejected"
                message = "❌ CGPA not found."
            elif cgpa < 6.5:
                cgpa_note = "below_threshold"
                cgpa_status = "Below threshold"
                status = "Rejected"
                message = f"❌ CGPA {cgpa} is below 6.5"
            else:
                cgpa_note = "ok"
                cgpa_status = "OK"
                # Do not auto-reject for missing skills — only notify
                status = "Shortlisted" if (skill_score is None or skill_score >= 0) else "Shortlisted"
                message = "✅ Resume processed."

            # Save history including skill-match details
            history.append({
                "cgpa": cgpa,
                "cgpa_status": cgpa_status,
                "exp": exp,
                "skills": skills,
                "required_skills": required_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "skill_score": skill_score,
                "score": overall_score,
                "status": status,
            })

        except Exception as e:
            tb = traceback.format_exc()
            print("=== Server Exception ===")
            print(tb)
            message = "Server error while processing the resume. If the problem persists, contact admin."
            status = "Rejected"
        finally:
            # cleanup
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass

    # render with extra values for template
    return render_template(
        "index.html",
        result=score,
        cgpa=cgpa,
        skills=skills,
        exp=exp,
        preview=preview,
        message=message,
        history=history
    )


if __name__ == "__main__":
    app.run(debug=True)
