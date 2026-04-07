# AI Resume Reviewer

[![Tests](https://github.com/Hassankusow/ai-resume-reviewer/actions/workflows/tests.yml/badge.svg)](https://github.com/Hassankusow/ai-resume-reviewer/actions/workflows/tests.yml)

A Streamlit web app that analyzes uploaded PDF resumes and gives instant, actionable feedback on ATS compatibility, section structure, action verb quality, keyword density, and readability — with optional AI-powered feedback via OpenAI.

---

## Features

- **ATS Score (0–100)** — scored across section completeness, keyword match, and length
- **Section Detection** — checks for Experience, Education, Skills, Projects, Summary, Certifications
- **Action Verb Analysis** — flags strong vs. weak verbs with counts
- **Keyword Density** — bar chart of top resume keywords
- **ATS Keyword Match** — checks against 25 common ATS keywords
- **Readability Checks** — detects quantifiable achievements, LinkedIn/GitHub URLs, long bullets
- **Rule-Based Feedback** — specific, numbered suggestions for improvement
- **AI Feedback** — optional GPT-4o-mini analysis via OpenAI API

---

## Tech Stack

- **Frontend:** Streamlit
- **PDF Parsing:** PyPDF2
- **Analysis:** Python (regex, collections, custom NLP logic)
- **Charts:** Matplotlib, NumPy
- **AI Feedback:** OpenAI API (optional)

---

## Project Structure

```
ai-resume-reviewer/
├── app.py           # Streamlit UI and dashboard
├── analyzer.py      # All analysis logic (sections, verbs, ATS, readability, OpenAI)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

**1. Clone and install**
```bash
git clone https://github.com/Hassankusow/ai-resume-reviewer
cd ai-resume-reviewer
pip install -r requirements.txt
```

**2. (Optional) Add OpenAI API key for AI feedback**
```bash
cp .env.example .env
# Add your key: OPENAI_API_KEY=your_key_here
```

**3. Run the app**
```bash
streamlit run app.py
```

Then upload any PDF resume — results appear instantly.

---

## How It Works

| Module | What it does |
|--------|-------------|
| `detect_sections()` | Scans for 7 standard resume sections by keyword matching |
| `analyze_action_verbs()` | Scores 30+ strong verbs, flags weak ones like "helped" or "assisted" |
| `analyze_keyword_density()` | Counts word frequency after stopword filtering |
| `compute_ats_score()` | 100-point score: 40pts sections + 40pts keywords + 20pts length |
| `analyze_readability()` | Checks for numbers, URLs, bullet length |
| `build_rule_based_feedback()` | Generates specific improvement suggestions |
| `get_openai_feedback()` | Calls GPT-4o-mini for AI-generated review (requires API key) |

---

## Author

**Hassan Abdi**
[GitHub](https://github.com/Hassankusow) | [LinkedIn](https://linkedin.com/in/hassan-abdi-119357267)
