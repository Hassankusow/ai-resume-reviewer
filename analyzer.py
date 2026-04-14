"""
Resume Analyzer
Handles section detection, action verb scoring, keyword density,
ATS scoring, readability metrics, and OpenAI feedback generation.
"""

import re
import os
from collections import Counter
from openai import OpenAI

# ─── Constants ────────────────────────────────────────────────────────────────

SECTION_KEYWORDS = {
    "experience":  ["experience", "work experience", "employment", "work history", "professional experience"],
    "education":   ["education", "academic background", "degrees", "university", "college"],
    "skills":      ["skills", "technical skills", "technologies", "competencies", "tools"],
    "projects":    ["projects", "personal projects", "academic projects", "portfolio"],
    "summary":     ["summary", "objective", "profile", "about me", "overview"],
    "certifications": ["certifications", "certificates", "licenses", "credentials"],
    "awards":      ["awards", "honors", "achievements", "accomplishments"],
}

STRONG_ACTION_VERBS = {
    "built", "designed", "developed", "implemented", "deployed", "engineered",
    "optimized", "reduced", "improved", "increased", "led", "managed", "created",
    "launched", "architected", "integrated", "automated", "streamlined", "delivered",
    "collaborated", "maintained", "migrated", "refactored", "scaled", "analyzed",
    "researched", "published", "presented", "mentored", "trained", "established",
    "coordinated", "spearheaded", "accelerated", "transformed", "drove", "generated",
}

WEAK_VERBS = {
    "helped", "assisted", "worked", "participated", "was responsible", "did",
    "handled", "used", "made", "tried", "attempted",
}

ATS_KEYWORDS = [
    "python", "javascript", "typescript", "java", "sql", "react", "node",
    "aws", "docker", "git", "api", "rest", "postgresql", "mongodb",
    "machine learning", "data analysis", "agile", "scrum", "ci/cd",
    "teamwork", "communication", "problem solving", "leadership",
]


# ─── Section Detection ────────────────────────────────────────────────────────

def detect_sections(text: str) -> dict:
    """Identify which standard resume sections are present."""
    text_lower = text.lower()
    found = {}
    for section, keywords in SECTION_KEYWORDS.items():
        found[section] = any(kw in text_lower for kw in keywords)
    return found


# ─── Action Verb Analysis ─────────────────────────────────────────────────────

def analyze_action_verbs(text: str) -> dict:
    words = re.findall(r"\b[a-z]+\b", text.lower())
    found_strong = [w for w in words if w in STRONG_ACTION_VERBS]
    found_weak   = [w for w in words if w in WEAK_VERBS]

    strong_counts = Counter(found_strong)
    weak_counts   = Counter(found_weak)

    score = min(100, len(set(found_strong)) * 8)  # up to 100, 8pts per unique strong verb

    return {
        "strong_verbs":       dict(strong_counts.most_common(10)),
        "weak_verbs":         dict(weak_counts.most_common(5)),
        "unique_strong_count": len(set(found_strong)),
        "weak_count":          len(found_weak),
        "score":               score,
    }


# ─── Keyword Density ──────────────────────────────────────────────────────────

def analyze_keyword_density(text: str, top_n: int = 20) -> dict:
    """Compute word frequency, filtering stopwords."""
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "this", "that", "these",
        "those", "i", "we", "you", "he", "she", "it", "they", "my", "our",
        "your", "their", "its", "as", "not", "no", "so", "if", "than", "then",
        "also", "into", "up", "out", "about", "using", "including",
    }
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in stopwords]
    counts = Counter(filtered)
    return {
        "top_keywords": dict(counts.most_common(top_n)),
        "total_words":  len(words),
        "unique_words": len(set(filtered)),
    }


# ─── ATS Score ────────────────────────────────────────────────────────────────

def compute_ats_score(text: str, sections: dict) -> dict:
    """
    Score the resume on ATS-friendliness:
    - Section completeness (40 pts)
    - ATS keyword presence (40 pts)
    - Length appropriateness (20 pts)
    """
    text_lower = text.lower()
    word_count = len(text.split())

    # Section score
    core_sections = ["experience", "education", "skills"]
    bonus_sections = ["projects", "summary", "certifications"]
    section_score = sum(12 for s in core_sections if sections.get(s))
    section_score += sum(7 for s in bonus_sections if sections.get(s))
    section_score = min(40, section_score)

    # Keyword score
    matched = [kw for kw in ATS_KEYWORDS if kw in text_lower]
    keyword_score = min(40, len(matched) * 3)

    # Length score (ideal: 300-700 words)
    if 300 <= word_count <= 700:
        length_score = 20
    elif 200 <= word_count < 300 or 700 < word_count <= 900:
        length_score = 12
    else:
        length_score = 5

    total = section_score + keyword_score + length_score

    return {
        "total_score":     total,
        "section_score":   section_score,
        "keyword_score":   keyword_score,
        "length_score":    length_score,
        "matched_keywords": matched,
        "word_count":      word_count,
    }


# ─── Readability ──────────────────────────────────────────────────────────────

def analyze_readability(text: str) -> dict:
    """Basic readability metrics."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    words = text.split()

    avg_sentence_len = len(words) / max(len(sentences), 1)

    # Flag overly long bullet points
    long_bullets = [s for s in sentences if len(s.split()) > 30]

    return {
        "sentence_count":    len(sentences),
        "avg_sentence_length": round(avg_sentence_len, 1),
        "long_bullets":       len(long_bullets),
        "has_numbers":        bool(re.search(r"\d+%|\d+x|\$\d+", text)),
        "has_email":          bool(re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)),
        "has_linkedin":       "linkedin" in text.lower(),
        "has_github":         "github" in text.lower(),
    }


# ─── Feedback Generation ──────────────────────────────────────────────────────

def build_rule_based_feedback(sections: dict, verbs: dict,
                               ats: dict, readability: dict):
    """Generate specific, actionable feedback without OpenAI."""
    feedback = []

    # Sections
    if not sections.get("summary"):
        feedback.append("Add a professional summary or objective at the top to help recruiters quickly understand your profile.")
    if not sections.get("skills"):
        feedback.append("Add a dedicated Skills section — ATS systems scan for this explicitly.")
    if not sections.get("projects"):
        feedback.append("Include a Projects section to showcase hands-on work, especially important for new grads.")

    # Action verbs
    if verbs["unique_strong_count"] < 5:
        feedback.append(f"Use more strong action verbs. Found only {verbs['unique_strong_count']} unique strong verbs. Aim for 8+.")
    if verbs["weak_count"] > 0:
        weak = list(verbs["weak_verbs"].keys())
        feedback.append(f"Replace weak verbs like {', '.join(weak)} with stronger alternatives (built, designed, optimized).")

    # ATS keywords
    if ats["keyword_score"] < 20:
        feedback.append("Low ATS keyword match. Add more technical skills and tools relevant to your target roles.")
    if ats["word_count"] < 300:
        feedback.append("Resume is too short. Aim for 300-700 words to give ATS enough content to parse.")
    if ats["word_count"] > 900:
        feedback.append("Resume is getting long. Try to trim to 1 page / under 700 words for entry-level roles.")

    # Readability
    if not readability["has_numbers"]:
        feedback.append("Add quantifiable achievements (e.g., 'improved performance by 40%', 'reduced runtime 3x'). Numbers stand out to recruiters.")
    if not readability["has_linkedin"]:
        feedback.append("Add your LinkedIn URL to your contact header.")
    if not readability["has_github"]:
        feedback.append("Add your GitHub URL — essential for software engineering roles.")
    if readability["long_bullets"] > 2:
        feedback.append(f"{readability['long_bullets']} bullet points exceed 30 words. Keep bullets concise (1-2 lines).")

    return feedback


def match_against_jd(resume_text: str, jd_text: str) -> dict:
    """
    Compare resume against a job description.
    Extracts meaningful terms from JD and scores how many appear in the resume.
    Returns match %, matched terms, and missing terms.
    """
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
        "have", "has", "had", "will", "would", "could", "should", "may", "can",
        "this", "that", "we", "you", "they", "our", "your", "their", "its",
        "as", "not", "also", "into", "up", "about", "using", "including",
        "experience", "work", "working", "knowledge", "ability", "skills",
        "required", "preferred", "plus", "strong", "excellent", "good",
        "must", "role", "team", "position", "candidate", "looking", "join",
        "help", "support", "build", "understand", "new", "high", "etc",
    }

    # Extract 1-gram and 2-gram terms from JD
    jd_lower = jd_text.lower()
    words = re.findall(r"\b[a-z][a-z0-9+#./-]{1,}\b", jd_lower)
    filtered = [w for w in words if w not in stopwords and len(w) >= 3]

    # Build bigrams (e.g. "machine learning", "ci/cd", "rest api")
    bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered) - 1)]

    # Score by frequency in JD — more frequent = more important
    term_counts = Counter(filtered + bigrams)

    # Take the top 40 most-mentioned terms as the "required" set
    jd_terms = [term for term, _ in term_counts.most_common(40)]

    resume_lower = resume_text.lower()
    matched = [t for t in jd_terms if t in resume_lower]
    missing = [t for t in jd_terms if t not in resume_lower]

    match_pct = round(len(matched) / len(jd_terms) * 100) if jd_terms else 0

    return {
        "match_pct":   match_pct,
        "matched":     matched,
        "missing":     missing[:15],   # top missing terms
        "total_jd_terms": len(jd_terms),
    }


def get_openai_feedback(resume_text: str, jd_text: str = None):
    """Call OpenAI API for AI-generated resume feedback. Returns None if no API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    if jd_text and jd_text.strip():
        system_msg = (
            "You are an expert resume coach and ATS specialist. "
            "A candidate is applying for the job described below. "
            "Review their resume and give 5-6 specific, actionable suggestions "
            "to better match this role. Call out missing keywords, weak framing, "
            "and quick wins. Be direct and specific."
        )
        user_msg = (
            f"JOB DESCRIPTION:\n{jd_text[:2000]}\n\n"
            f"RESUME:\n{resume_text[:2500]}"
        )
    else:
        system_msg = (
            "You are an expert resume coach and technical recruiter. "
            "Analyze the resume and provide 5-6 specific, actionable suggestions "
            "to improve it for software engineering roles. Be concise and direct."
        )
        user_msg = f"Please review this resume:\n\n{resume_text[:3000]}"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=700,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI feedback unavailable: {str(e)}"


# ─── Full Analysis ────────────────────────────────────────────────────────────

def analyze_resume(text: str, jd_text: str = None) -> dict:
    """Run all analysis passes and return a complete report."""
    sections    = detect_sections(text)
    verbs       = analyze_action_verbs(text)
    keywords    = analyze_keyword_density(text)
    ats         = compute_ats_score(text, sections)
    readability = analyze_readability(text)
    feedback    = build_rule_based_feedback(sections, verbs, ats, readability)
    ai_feedback = get_openai_feedback(text, jd_text)
    jd_match    = match_against_jd(text, jd_text) if jd_text and jd_text.strip() else None

    return {
        "sections":    sections,
        "verbs":       verbs,
        "keywords":    keywords,
        "ats":         ats,
        "readability": readability,
        "feedback":    feedback,
        "ai_feedback": ai_feedback,
        "jd_match":    jd_match,
    }
