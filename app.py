@app.route("/", methods=["GET", "POST"])
def home():
    score = None
    cgpa = None
    shortlisted = False
    message = ""

    if request.method == "POST":
        jd = request.form["job_desc"]
        file = request.files["resume"]

        ext = file.filename.split(".")[-1].lower()
        path = f"temp.{ext}"
        file.save(path)

        # extract text
        if ext == "pdf":
            resume_text = extract_from_pdf(path)
        else:
            resume_text = extract_from_docx(path)

        # ---- CGPA EXTRACTION ----
        cgpa = extract_cgpa(resume_text)

        if cgpa is None:
            message = "CGPA not found in resume"
            shortlisted = False
        elif cgpa < 6.5:
            message = f"Rejected: CGPA {cgpa} is below 6.5"
            shortlisted = False
        else:
            # If CGPA is valid, do AI matching
            score = matcher.calculate_score(resume_text, jd)
            shortlisted = True
            message = f"Shortlisted! CGPA: {cgpa}"

    return render_template("index.html", result=score, cgpa=cgpa, shortlisted=shortlisted, message=message)

