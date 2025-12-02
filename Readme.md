# 📄 AI Resume Reviewer

AI Resume Reviewer is a Streamlit-based web app that analyzes uploaded resumes (PDF) for structure, keyword density, and readability. It uses NLP techniques to identify common resume gaps and suggest improvements — helping job seekers better tailor their resumes for recruiters and applicant tracking systems (ATS).

---

## 🚀 Features

- 📄 Upload and preview PDF resumes
- 🔍 Extract and analyze resume text
- 🧠 Evaluate keyword usage, section structure, and action verbs
- ✍️ Provide feedback and suggestions (via OpenAI or rule-based logic)
- 📊 Visualize resume data (coming soon)

---

## 📆 Tech Stack

- **Frontend:** Streamlit
- **Backend/NLP:** Python, spaCy or OpenAI API
- **PDF Parsing:** PyMuPDF (`fitz`) or PyPDF2

---

## 📂 Project Structure

```
ai-resume-reviewer/
├── app.py               # Main Streamlit app
├── analyzer.py          # Scoring & NLP logic
├── utils.py             # PDF/text parsing helpers
├── sample_resume.pdf    # Sample for testing
├── requirements.txt     # Python dependencies
└── README.md            # Project overview
```

---

## ⚙️ Setup Instructions

1. **Clone the repo** and navigate into it:

```bash
git clone https://github.com/your-username/ai-resume-reviewer
cd ai-resume-reviewer
```

2. **Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the app:**

```bash
streamlit run app.py
```

---

## 📌 Sample Use Case

1. Upload your resume (PDF)
2. See extracted text preview
3. Review detected structure and keyword feedback
4. Improve your resume for recruiter readability and ATS parsing

---

## ✅ Future Improvements

- Resume scoring based on ATS guidelines
- Integration with job descriptions for keyword matching
- Downloadable feedback reports
- Visual analytics (word clouds, section heatmaps)

---

## 🙌 Contributing

Pull requests are welcome!
Feel free to open an issue or submit a PR to improve scoring, add better NLP checks, or enhance the UI.

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Hassan Abdi**
[GitHub](https://github.com/Hassankusow) | [LinkedIn](https://www.linkedin.com/in/hassan-abdi-119357267)
