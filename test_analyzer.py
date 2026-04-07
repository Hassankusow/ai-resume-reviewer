"""
Tests for the AI Resume Reviewer analyzer module.
Run with: pytest test_analyzer.py -v
"""

import pytest
from analyzer import (
    detect_sections,
    analyze_action_verbs,
    analyze_keyword_density,
    compute_ats_score,
    analyze_readability,
    build_rule_based_feedback,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def strong_resume():
    return """
    Hassan Abdi
    hassan@example.com | github.com/hassan | linkedin.com/in/hassan

    SUMMARY
    Experienced software engineer with strong background in cloud systems.

    EXPERIENCE
    Software Engineer — MyCritters Inc.
    Built and deployed a cloud-native platform using React, Node.js, and PostgreSQL.
    Optimized database queries, reducing response time by 40%.
    Designed and implemented a real-time Kanban board with role-based access control.
    Integrated AI-powered semantic search using OpenAI embeddings API.
    Improved SEO and performance, resulting in a 200% increase in site traffic.

    EDUCATION
    Portland State University — B.S. Computer Science

    SKILLS
    Python, JavaScript, TypeScript, SQL, React, Node.js, PostgreSQL, Docker, AWS, Git

    PROJECTS
    AI Resume Reviewer — Python, Streamlit, NLP
    Developed an AI-powered web app analyzing resumes using OpenAI API and machine learning.
    """


@pytest.fixture
def weak_resume():
    return """
    John Doe

    EXPERIENCE
    Helped with some tasks.
    Assisted the team with various responsibilities.
    Worked on the project.
    Participated in meetings.
    """


# ─── Section Detection ────────────────────────────────────────────────────────

class TestDetectSections:

    def test_detects_experience(self, strong_resume):
        sections = detect_sections(strong_resume)
        assert sections["experience"] is True

    def test_detects_education(self, strong_resume):
        sections = detect_sections(strong_resume)
        assert sections["education"] is True

    def test_detects_skills(self, strong_resume):
        sections = detect_sections(strong_resume)
        assert sections["skills"] is True

    def test_detects_projects(self, strong_resume):
        sections = detect_sections(strong_resume)
        assert sections["projects"] is True

    def test_detects_summary(self, strong_resume):
        sections = detect_sections(strong_resume)
        assert sections["summary"] is True

    def test_missing_sections_return_false(self, weak_resume):
        sections = detect_sections(weak_resume)
        assert sections["skills"] is False
        assert sections["education"] is False

    def test_returns_all_section_keys(self, strong_resume):
        sections = detect_sections(strong_resume)
        for key in ("experience", "education", "skills", "projects", "summary", "certifications", "awards"):
            assert key in sections

    def test_case_insensitive(self):
        text = "EXPERIENCE\nSKILLS\nEDUCATION"
        sections = detect_sections(text)
        assert sections["experience"] is True
        assert sections["skills"] is True
        assert sections["education"] is True


# ─── Action Verb Analysis ─────────────────────────────────────────────────────

class TestAnalyzeActionVerbs:

    def test_detects_strong_verbs(self, strong_resume):
        result = analyze_action_verbs(strong_resume)
        assert result["unique_strong_count"] > 0

    def test_detects_weak_verbs(self, weak_resume):
        result = analyze_action_verbs(weak_resume)
        assert result["weak_count"] > 0

    def test_strong_resume_high_score(self, strong_resume):
        result = analyze_action_verbs(strong_resume)
        assert result["score"] > 40

    def test_weak_resume_low_score(self, weak_resume):
        result = analyze_action_verbs(weak_resume)
        assert result["score"] < 40

    def test_score_capped_at_100(self):
        verbs = " ".join(["built designed developed implemented deployed optimized "
                          "reduced improved increased led managed created launched "
                          "architected integrated automated streamlined"] * 3)
        result = analyze_action_verbs(verbs)
        assert result["score"] <= 100

    def test_returns_expected_keys(self, strong_resume):
        result = analyze_action_verbs(strong_resume)
        for key in ("strong_verbs", "weak_verbs", "unique_strong_count", "weak_count", "score"):
            assert key in result


# ─── Keyword Density ──────────────────────────────────────────────────────────

class TestAnalyzeKeywordDensity:

    def test_returns_top_keywords(self, strong_resume):
        result = analyze_keyword_density(strong_resume)
        assert len(result["top_keywords"]) > 0

    def test_filters_stopwords(self, strong_resume):
        result = analyze_keyword_density(strong_resume)
        stopwords = {"the", "and", "or", "in", "a", "an"}
        for word in result["top_keywords"]:
            assert word not in stopwords

    def test_total_word_count_positive(self, strong_resume):
        result = analyze_keyword_density(strong_resume)
        assert result["total_words"] > 0

    def test_unique_words_leq_total(self, strong_resume):
        result = analyze_keyword_density(strong_resume)
        assert result["unique_words"] <= result["total_words"]

    def test_top_n_respected(self, strong_resume):
        result = analyze_keyword_density(strong_resume, top_n=5)
        assert len(result["top_keywords"]) <= 5


# ─── ATS Score ────────────────────────────────────────────────────────────────

class TestComputeAtsScore:

    def test_strong_resume_high_score(self, strong_resume):
        sections = detect_sections(strong_resume)
        result = compute_ats_score(strong_resume, sections)
        assert result["total_score"] >= 50

    def test_weak_resume_low_score(self, weak_resume):
        sections = detect_sections(weak_resume)
        result = compute_ats_score(weak_resume, sections)
        assert result["total_score"] < 50

    def test_score_within_0_to_100(self, strong_resume):
        sections = detect_sections(strong_resume)
        result = compute_ats_score(strong_resume, sections)
        assert 0 <= result["total_score"] <= 100

    def test_returns_expected_keys(self, strong_resume):
        sections = detect_sections(strong_resume)
        result = compute_ats_score(strong_resume, sections)
        for key in ("total_score", "section_score", "keyword_score", "length_score",
                    "matched_keywords", "word_count"):
            assert key in result

    def test_section_score_capped_at_40(self, strong_resume):
        sections = detect_sections(strong_resume)
        result = compute_ats_score(strong_resume, sections)
        assert result["section_score"] <= 40

    def test_keyword_score_capped_at_40(self, strong_resume):
        sections = detect_sections(strong_resume)
        result = compute_ats_score(strong_resume, sections)
        assert result["keyword_score"] <= 40


# ─── Readability ──────────────────────────────────────────────────────────────

class TestAnalyzeReadability:

    def test_detects_email(self):
        result = analyze_readability("Contact: hassan@example.com")
        assert result["has_email"] is True

    def test_detects_linkedin(self):
        result = analyze_readability("linkedin.com/in/hassan")
        assert result["has_linkedin"] is True

    def test_detects_github(self):
        result = analyze_readability("github.com/hassan")
        assert result["has_github"] is True

    def test_detects_numbers(self):
        result = analyze_readability("Improved performance by 40%")
        assert result["has_numbers"] is True

    def test_no_false_positives(self):
        result = analyze_readability("Just plain text with no contact info.")
        assert result["has_email"] is False
        assert result["has_linkedin"] is False
        assert result["has_github"] is False
        assert result["has_numbers"] is False

    def test_returns_expected_keys(self, strong_resume):
        result = analyze_readability(strong_resume)
        for key in ("sentence_count", "avg_sentence_length", "long_bullets",
                    "has_numbers", "has_email", "has_linkedin", "has_github"):
            assert key in result


# ─── Feedback Generation ──────────────────────────────────────────────────────

class TestBuildRuleBasedFeedback:

    def test_weak_resume_generates_feedback(self, weak_resume):
        sections    = detect_sections(weak_resume)
        verbs       = analyze_action_verbs(weak_resume)
        ats         = compute_ats_score(weak_resume, sections)
        readability = analyze_readability(weak_resume)
        feedback    = build_rule_based_feedback(sections, verbs, ats, readability)
        assert len(feedback) > 0

    def test_feedback_items_are_strings(self, weak_resume):
        sections    = detect_sections(weak_resume)
        verbs       = analyze_action_verbs(weak_resume)
        ats         = compute_ats_score(weak_resume, sections)
        readability = analyze_readability(weak_resume)
        feedback    = build_rule_based_feedback(sections, verbs, ats, readability)
        assert all(isinstance(f, str) for f in feedback)

    def test_strong_resume_less_feedback(self, strong_resume, weak_resume):
        def get_feedback(text):
            s = detect_sections(text)
            v = analyze_action_verbs(text)
            a = compute_ats_score(text, s)
            r = analyze_readability(text)
            return build_rule_based_feedback(s, v, a, r)
        assert len(get_feedback(strong_resume)) <= len(get_feedback(weak_resume))
