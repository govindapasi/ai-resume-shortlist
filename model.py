# model.py
import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")  # keep alphanumerics

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    tokens = TOKEN_RE.findall(text)
    # optional: remove very short tokens
    tokens = [t for t in tokens if len(t) > 1]
    return tokens

def term_freq(tokens):
    return Counter(tokens)

def cosine_similarity_from_counters(c1, c2):
    # dot product
    dot = 0
    for k, v in c1.items():
        dot += v * c2.get(k, 0)
    # magnitudes
    mag1 = math.sqrt(sum(v*v for v in c1.values()))
    mag2 = math.sqrt(sum(v*v for v in c2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

class ResumeMatcher:
    def __init__(self):
        pass

    def calculate_score(self, resume_text, jd_text):
        # simple pipeline: normalize -> term frequency -> cosine
        rtoks = normalize_text(resume_text or "")
        jtoks = normalize_text(jd_text or "")
        c1 = term_freq(rtoks)
        c2 = term_freq(jtoks)
        sim = cosine_similarity_from_counters(c1, c2)
        # convert to percentage 0-100
        return round(sim * 100, 2)
