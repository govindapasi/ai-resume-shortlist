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
    skills = None
    exp = None
    preview = None
    message = ""
    status = None

    if request.method == "POST":
        try:
            jd = request.form.get("job_desc", "")
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

            # Try to get size safely
            file_stream = file.stream
            file_stream.seek(0, os.SEEK_END)
            size = file_stream.tell()
            file_stream.seek(0)
            if size and size > MAX_UPLOAD_BYTES:
                message = f"File too large ({round(size/1e6,2)} MB). Max allowed ≈4.5 MB."
                status = "Rejected"
                return render_template("index.html", result=score, cgpa=cgpa, skills=skills,
                                       exp=exp, preview=preview, message=message, history=history)

            # Save to a safe temporary path with unique name
            unique_name = f"upload_{uuid.uuid4().hex}.{ext}"
            temp_dir = "/tmp" if os.path.exists("/tmp") else "."
            temp_path = os.path.join(temp_dir, unique_name)
            safe_save_file(file, temp_path)

            # Extract text depending on type
            resume_text = ""
            if ext == "pdf":
                try:
                    resume_text = extract_from_pdf(temp_path)
                except Exception as e:
                    raise RuntimeError(f"PDF parsing failed: {e}")
            else:  # docx
                try:
                    resume_text = extract_from_docx(temp_path)
                except Exception as e:
                    raise RuntimeError(f"DOCX parsing failed: {e}")

            preview = (resume_text or "")[:2000]
            cgpa = extract_cgpa(resume_text)
            exp = extract_experience(resume_text)
            skills = extract_skills(resume_text)

            # Shortlisting logic
            if cgpa is None:
                message = "❌ CGPA not found."
                status = "Rejected"
            elif cgpa < 6.5:
                message = f"❌ CGPA {cgpa} is below 6.5"
                status = "Rejected"
            else:
                score = matcher.calculate_score(resume_text, jd)
                message = "✅ Shortlisted!"
                status = "Shortlisted"

            # Save history
            history.append({
                "cgpa": cgpa,
                "exp": exp,
                "skills": skills,
                "score": score,
                "status": status,
            })

        except Exception as e:
            # Log full traceback to server logs (Vercel console)
            tb = traceback.format_exc()
            print("=== Server Exception ===")
            print(tb)
            # Show friendly error to user (do not expose full traceback in production)
            message = "Server error while processing the resume. If the problem persists, check the file or contact admin."
            status = "Rejected"
        finally:
            # Clean up the temp file if it exists
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

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
