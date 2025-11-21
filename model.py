import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

def normalize(text):
    text = text.lower()
    return TOKEN_RE.findall(text)

def tf(tokens):
    return Counter(tokens)

def cosine(c1, c2):
    dot = sum(v * c2.get(k, 0) for k, v in c1.items())
    mag1 = math.sqrt(sum(v*v for v in c1.values()))
    mag2 = math.sqrt(sum(v*v for v in c2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

class ResumeMatcher:
    def calculate_score(self, resume_text, jd_text):
        r = normalize(resume_text)
        j = normalize(jd_text)
        c1 = tf(r)
        c2 = tf(j)
        return round(cosine(c1, c2) * 100, 2)


        return round(sim * 100, 2)
