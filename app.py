import streamlit as st
import PyPDF2
import matplotlib.pyplot as plt
import numpy as np
from analyzer import analyze_resume

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume Reviewer",
    page_icon="📄",
    layout="wide",
)

# ─── Header ──────────────────────────────────────────────────────────────────

st.title("📄 AI Resume Reviewer")
st.markdown("Upload your resume and paste a job description to see exactly how you score against the role — just like real ATS systems.")
st.divider()

# ─── Inputs ──────────────────────────────────────────────────────────────────

col_upload, col_jd = st.columns([1, 1])

with col_upload:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

with col_jd:
    jd_text = st.text_area(
        "Paste job description (optional but recommended)",
        height=160,
        placeholder="Paste the full job posting here — we'll score your resume against the exact keywords and requirements this company is looking for.",
    )

if uploaded_file is None:
    st.info("Upload a PDF resume to get started.")
    st.stop()

# ─── Parse PDF ───────────────────────────────────────────────────────────────

try:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text() or ""
except Exception as e:
    st.error(f"Failed to read PDF: {e}")
    st.stop()

if not resume_text.strip():
    st.error("Could not extract text from this PDF. Try a different file.")
    st.stop()

# ─── Run Analysis ────────────────────────────────────────────────────────────

with st.spinner("Analyzing your resume..."):
    report = analyze_resume(resume_text, jd_text if jd_text and jd_text.strip() else None)

ats         = report["ats"]
verbs       = report["verbs"]
keywords    = report["keywords"]
sections    = report["sections"]
readability = report["readability"]
feedback    = report["feedback"]
ai_feedback = report["ai_feedback"]
jd_match    = report["jd_match"]

# ─── Score Overview ───────────────────────────────────────────────────────────

st.subheader("📊 Overall ATS Score")

score = ats["total_score"]
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("ATS Score", f"{score}/100",
              delta="Strong" if score >= 75 else ("Moderate" if score >= 50 else "Needs Work"))
with col2:
    st.metric("Word Count", ats["word_count"],
              delta="Good" if 300 <= ats["word_count"] <= 700 else "Adjust length")
with col3:
    st.metric("Strong Action Verbs", verbs["unique_strong_count"],
              delta="Good" if verbs["unique_strong_count"] >= 8 else "Add more")
with col4:
    st.metric("ATS Keywords Matched", len(ats["matched_keywords"]))

# Score progress bar
fig, ax = plt.subplots(figsize=(10, 1.2))
color = "#2ecc71" if score >= 75 else ("#f39c12" if score >= 50 else "#e74c3c")
ax.barh(["Score"], [score],       color=color,    height=0.5)
ax.barh(["Score"], [100 - score], left=[score], color="#ecf0f1", height=0.5)
ax.set_xlim(0, 100)
ax.axvline(75, color="green",  linestyle="--", linewidth=1, alpha=0.6, label="Good (75)")
ax.axvline(50, color="orange", linestyle="--", linewidth=1, alpha=0.6, label="Moderate (50)")
ax.set_xlabel("ATS Score")
ax.legend(fontsize=7, loc="upper left")
ax.set_title(f"ATS Score: {score}/100", fontsize=10)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ─── JD Match ────────────────────────────────────────────────────────────────

if jd_match:
    st.subheader("🎯 Job Description Match")

    pct = jd_match["match_pct"]
    color = "#2ecc71" if pct >= 70 else ("#f39c12" if pct >= 45 else "#e74c3c")
    label = "Strong match" if pct >= 70 else ("Moderate match" if pct >= 45 else "Low match — needs work"  )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("JD Match Score", f"{pct}%", delta=label)
    with col2:
        st.metric("Keywords Matched", len(jd_match["matched"]))
    with col3:
        st.metric("Keywords Missing", len(jd_match["missing"]))

    fig, ax = plt.subplots(figsize=(10, 1.0))
    ax.barh(["Match"], [pct],       color=color,    height=0.5)
    ax.barh(["Match"], [100 - pct], left=[pct],   color="#ecf0f1", height=0.5)
    ax.set_xlim(0, 100)
    ax.axvline(70, color="green",  linestyle="--", linewidth=1, alpha=0.6, label="Strong (70%)")
    ax.axvline(45, color="orange", linestyle="--", linewidth=1, alpha=0.6, label="Moderate (45%)")
    ax.set_xlabel("Match %")
    ax.legend(fontsize=7, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    col_matched, col_missing = st.columns(2)
    with col_matched:
        st.markdown("**✅ Keywords found in your resume:**")
        if jd_match["matched"]:
            st.success("  ".join(f"`{k}`" for k in jd_match["matched"]))
        else:
            st.warning("No JD keywords found in your resume.")
    with col_missing:
        st.markdown("**❌ Keywords missing from your resume:**")
        if jd_match["missing"]:
            st.error("  ".join(f"`{k}`" for k in jd_match["missing"]))
        else:
            st.success("You're covering all the key terms!")

    st.divider()
else:
    st.info("💡 Paste a job description above to see how your resume scores against this specific role.")
    st.divider()

# ─── Section & Contact ───────────────────────────────────────────────────────

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Section Detection")
    for section, found in sections.items():
        icon = "✅" if found else "❌"
        st.markdown(f"{icon} **{section.capitalize()}**")

with col_right:
    st.subheader("📞 Contact Info")
    st.markdown(f"{'✅' if readability['has_email'] else '❌'} Email detected")
    st.markdown(f"{'✅' if readability['has_linkedin'] else '❌'} LinkedIn URL")
    st.markdown(f"{'✅' if readability['has_github'] else '❌'} GitHub URL")
    st.markdown(f"{'✅' if readability['has_numbers'] else '❌'} Quantifiable achievements (numbers/percentages)")

st.divider()

# ─── Action Verb Analysis ─────────────────────────────────────────────────────

st.subheader("💪 Action Verb Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Strong verbs found:**")
    if verbs["strong_verbs"]:
        for verb, count in list(verbs["strong_verbs"].items())[:8]:
            st.markdown(f"&nbsp;&nbsp;✅ `{verb}` ×{count}")
    else:
        st.warning("No strong action verbs detected.")

with col2:
    st.markdown("**Weak verbs to replace:**")
    if verbs["weak_verbs"]:
        for verb, count in verbs["weak_verbs"].items():
            st.markdown(f"&nbsp;&nbsp;⚠️ `{verb}` ×{count}")
    else:
        st.success("No weak verbs detected.")

st.divider()

# ─── Keyword Density ──────────────────────────────────────────────────────────

st.subheader("🔑 Top Keywords")

top_kw = list(keywords["top_keywords"].items())[:15]
if top_kw:
    words_list  = [k for k, _ in top_kw]
    counts_list = [v for _, v in top_kw]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(words_list[::-1], counts_list[::-1], color="steelblue")
    ax.set_xlabel("Frequency")
    ax.set_title("Top Keywords in Resume")
    for i, (w, c) in enumerate(zip(words_list[::-1], counts_list[::-1])):
        ax.text(c + 0.1, i, str(c), va="center", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("**ATS Keywords Matched:**")
if ats["matched_keywords"]:
    st.success(", ".join(f"`{k}`" for k in ats["matched_keywords"]))
else:
    st.warning("No common ATS keywords found. Add relevant technical skills.")

st.divider()

# ─── Score Breakdown Chart ────────────────────────────────────────────────────

st.subheader("📈 Score Breakdown")

categories = ["Sections\n(40 max)", "ATS Keywords\n(40 max)", "Length\n(20 max)"]
scored     = [ats["section_score"], ats["keyword_score"], ats["length_score"]]
max_scores = [40, 40, 20]

fig, ax = plt.subplots(figsize=(8, 3.5))
x = np.arange(len(categories))
ax.bar(x, max_scores, color="#ecf0f1", label="Max possible")
ax.bar(x, scored,     color="#3498db",  label="Your score", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.set_ylabel("Points")
ax.set_title("ATS Score Breakdown")
ax.legend(fontsize=8)
for i, (s, m) in enumerate(zip(scored, max_scores)):
    ax.text(i, s + 0.5, f"{s}/{m}", ha="center", fontsize=9, fontweight="bold")
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ─── Actionable Feedback ──────────────────────────────────────────────────────

st.subheader("✏️ Actionable Feedback")

if feedback:
    for i, tip in enumerate(feedback, 1):
        st.warning(f"**{i}.** {tip}")
else:
    st.success("Your resume looks strong! No major issues detected.")

# ─── AI Feedback ─────────────────────────────────────────────────────────────

st.subheader("🤖 AI-Powered Feedback")

if ai_feedback:
    st.info(ai_feedback)
else:
    st.info(
        "AI feedback requires an OpenAI API key. "
        "Add `OPENAI_API_KEY=your_key` to a `.env` file in this directory to enable it."
    )

st.divider()

# ─── Raw Text Preview ────────────────────────────────────────────────────────

with st.expander("📄 View Extracted Resume Text"):
    st.text_area("Extracted Text", resume_text, height=300)
