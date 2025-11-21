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


/* =====================================================
   LIGHT PARALLAX EFFECT FOR BACKGROUND ELEMENTS (if any)
   ===================================================== */

window.addEventListener("scroll", function () {
    const scrolled = window.pageYOffset;
    document.body.style.backgroundPositionY = -(scrolled * 0.1) + "px";
});
