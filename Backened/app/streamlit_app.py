import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Skill Match AI",
    layout="wide"
)

st.title("Skill Match AI Resume Screening")

# ==========================================================
# Create Job
# ==========================================================

st.header("1. Create Job")

title = st.text_input("Job Title")

jd_text = st.text_area(
    "Job Description",
    height=250
)

if st.button("Create Job"):

    payload = {
        "title": title,
        "raw_text": jd_text
    }

    response = requests.post(
        f"{API_BASE}/jobs",
        json=payload
    )

    if response.status_code == 201:

        data = response.json()

        st.success(f"Job Created")

        st.session_state["job_id"] = data["job_id"]

        st.write("Job ID:", data["job_id"])

    else:

        st.error(response.text)


# ==========================================================
# Upload Candidates
# ==========================================================

st.header("2. Upload Resumes")

job_id = st.text_input(
    "Job ID",
    value=st.session_state.get("job_id", "")
)

uploaded_files = st.file_uploader(
    "Upload PDF Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Process Resumes"):

    if not job_id:
        st.error("Job ID required")

    elif not uploaded_files:
        st.error("Upload at least one PDF")

    else:

        files = []

        for file in uploaded_files:
            files.append(
                ("files", (file.name, file.getvalue(), "application/pdf"))
            )

        response = requests.post(
            f"{API_BASE}/candidates/{job_id}",
            files=files
        )

        if response.status_code == 200:

            st.success("Resumes submitted")

            st.json(response.json())

        else:

            st.error(response.text)


# ==========================================================
# Rank Candidates
# ==========================================================

st.header("3. Rank Candidates")

rank_job_id = st.text_input(
    "Rank Job ID",
    value=st.session_state.get("job_id", "")
)

if st.button("Run Ranking"):

    response = requests.post(
        f"{API_BASE}/rank/{rank_job_id}"
    )

    if response.status_code == 200:

        st.success("Ranking complete")

        st.json(response.json())

    else:

        st.error(response.text)


# ==========================================================
# View Candidates
# ==========================================================

st.header("4. View Ranked Candidates")

view_job_id = st.text_input(
    "View Job ID",
    value=st.session_state.get("job_id", "")
)

page = st.number_input(
    "Page",
    min_value=1,
    value=1
)

limit = st.number_input(
    "Limit",
    min_value=1,
    max_value=100,
    value=20
)

if st.button("Fetch Candidates"):

    response = requests.get(
        f"{API_BASE}/candidates/{view_job_id}",
        params={
            "page": page,
            "limit": limit
        }
    )

    if response.status_code == 200:

        data = response.json()

        st.write("Total Candidates:", data["total"])

        for candidate in data["candidates"]:

            st.write(candidate)

    else:

        st.error(response.text)