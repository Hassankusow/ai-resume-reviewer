import streamlit as st
import PyPDF2

st.set_page_config(page_title="AI Resume Reviewer", layout="centered")

st.title("📄 AI Resume Reviewer")
st.subheader("Upload your resume (PDF) and get instant feedback")

uploaded_file = st.file_uploader("Choose your resume (PDF)", type="pdf")

if uploaded_file is not None:
    # Read text from PDF
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        
        st.success("Resume uploaded and parsed successfully!")
        st.subheader("Extracted Text Preview")
        st.text_area("Resume Text", resume_text, height=300)

    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
