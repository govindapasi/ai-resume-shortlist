/* =====================================================
   SCROLL REVEAL ANIMATIONS
   ===================================================== */

/* 
   This script watches elements with:
   .fade-in
   .fade-in-up
   .glass
   .feature-card
   .summary-card
   .upload-form
*/

const revealElements = document.querySelectorAll(
    ".fade-in, .fade-in-up, .feature-card, .summary-card, .upload-form, .result-box"
);

function revealOnScroll() {
    const windowHeight = window.innerHeight;

    revealElements.forEach((el) => {
        const elementTop = el.getBoundingClientRect().top;

        if (elementTop < windowHeight - 80) {
            el.classList.add("visible");
        }
    });
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);


/* =====================================================
   ADD SMOOTH FLOATING EFFECT TO HERO TITLE
   ===================================================== */

const heroTitle = document.querySelector(".hero-title");
if (heroTitle) {
    window.addEventListener("scroll", () => {
        const offset = window.scrollY * 0.1;
        heroTitle.style.transform = `translateY(${offset}px)`;
    });
}


/* =====================================================
   NAVBAR SCROLL EFFECT
   ===================================================== */

const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
    if (window.scrollY > 80) {
        navbar.style.background = "rgba(0,0,0,0.75)";
        navbar.style.backdropFilter = "blur(12px)";
    } else {
        navbar.style.background = "rgba(0,0,0,0.45)";
        navbar.style.backdropFilter = "blur(6px)";
    }
});


/* =====================================================
   SMOOTH SCROLL FOR ALL INTERNAL LINKS
   ===================================================== */

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    });
});

/* ============================
   Feature Panel: open/close + content
   ============================ */

const featureContents = {
    cgpa: {
        title: "CGPA Filtering",
        desc: "Automatically filter candidates by CGPA. Only resumes with CGPA ≥ 6.5 pass this filter.",
        bullets: [
            "Parses multiple formats: 'CGPA: 7.5', '8.2/10', '3.6/4.0 (converted)'.",
            "Converts 4.0 scale to 10 scale automatically.",
            "Helps HR reduce manual filtering and enforce baseline criteria.",
            "If CGPA not found, system shows 'CGPA not found' and marks candidate rejected."
        ]
    },
    ai: {
        title: "AI Matching",
        desc: "We calculate a similarity score between the resume text and the job description using lightweight semantic matching.",
        bullets: [
            "Tokenizes text and computes cosine similarity for relevance score (0–100%).",
            "Highlights matched keywords (in preview) so HR can see why a candidate scored high.",
            "Fast and explainable — no heavy models required for quick screening.",
            "Score is used as supportive signal — combine with human judgement."
        ]
    },
    skills: {
        title: "Skill Extraction",
        desc: "Automatic detection of common skills such as Python, SQL, React and more.",
        bullets: [
            "Compares resume text against a curated skill list.",
            "Displays skills in the results and dashboard for quick filtering.",
            "Easily extend the skill list in `app.py` for domain-specific roles.",
            "Helps recruiters quickly identify candidates with required technical abilities."
        ]
    },
    experience: {
        title: "Experience Detection",
        desc: "Detects phrases like '3 years' or '5+ years' to estimate total experience.",
        bullets: [
            "Extracts numeric 'X years' mentions from resume text.",
            "Shows experience in the Preview and Dashboard.",
            "Useful for role-level filtering (junior vs senior)."
        ]
    },
    preview: {
        title: "Resume Preview",
        desc: "Preview the extracted resume text directly in the UI.",
        bullets: [
            "Shows the first part of the parsed text with matched keywords.",
            "Avoids opening attachments one-by-one.",
            "Copy important sections for reporting or notes."
        ]
    },
    history: {
        title: "Shortlist History",
        desc: "A stored list of all previously analyzed resumes displayed in the dashboard.",
        bullets: [
            "Shows CGPA, experience, skills, score and status for each candidate.",
            "Use dashboard filters to find shortlisted candidates quickly.",
            "History is in-memory by default; can be moved to a database for persistence."
        ]
    }
};

function openFeaturePanel(key) {
    const panel = document.getElementById("feature-panel");
    const titleEl = document.getElementById("feature-title");
    const descEl = document.getElementById("feature-desc");
    const detailsEl = document.getElementById("feature-details");

    const content = featureContents[key];
    if (!content) return;

    // populate
    titleEl.textContent = content.title;
    descEl.textContent = content.desc;

    // build bullets
    detailsEl.innerHTML = "<ul>" + content.bullets.map(b => `<li>${b}</li>`).join("") + "</ul>";

    // open panel
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");

    // focus on close button for accessibility
    document.getElementById("feature-close").focus();
}

function closeFeaturePanel() {
    const panel = document.getElementById("feature-panel");
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
}

// attach click handlers to feature cards
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".feature-card").forEach(card => {
        card.addEventListener("click", () => {
            const key = card.getAttribute("data-feature");
            openFeaturePanel(key);
        });
        // keyboard accessible
        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                const key = card.getAttribute("data-feature");
                openFeaturePanel(key);
            }
        });
    });

    // close buttons
    const closeBtn = document.getElementById("feature-close");
    const gotit = document.getElementById("feature-gotit");
    if (closeBtn) closeBtn.addEventListener("click", closeFeaturePanel);
    if (gotit) gotit.addEventListener("click", closeFeaturePanel);

    // close on Escape
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeFeaturePanel();
    });
});

/* =====================================================
   LIGHT PARALLAX EFFECT FOR BACKGROUND ELEMENTS (if any)
   ===================================================== */

window.addEventListener("scroll", function () {
    const scrolled = window.pageYOffset;
    document.body.style.backgroundPositionY = -(scrolled * 0.1) + "px";
});
