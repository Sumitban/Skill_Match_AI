import streamlit as st

from Backened.app.storage.jobs_repo import JobRepository


# getting all the jobs
jobs_instance = JobRepository()
jobs = jobs_instance.get_jobs()
jobs_title = [job["title"] for job in jobs]
jobs_id = [job["job_id"] for job in jobs]

st.selectbox("Select a job:", options=jobs_title, key="job_selectbox")
