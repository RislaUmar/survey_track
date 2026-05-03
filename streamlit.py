import streamlit as st

# PAGE SETUP
about_page = st.Page(
    page="views/about.py",
    title="About",
    icon=":material/account_circle:",
    
)

project_1_page = st.Page(
    page="views/survey_progress.py",
    title="Survey Progress",
    icon=":material/pace:",
    default=True
)

project_2_page = st.Page(
    page="views/timeuse_summary.py",
    title="Time Use Summary",
    icon=":material/overview:"
)

# NAVIGATION SETUP 
pg = st.navigation(pages=[about_page, project_1_page, project_2_page]) # (WITHOUT SECTION)

pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_1_page, project_2_page]
    }
) # (WITH SECTION)

# Shared on all pages
# st.logo("assets/logo.jpg")

# st.sidebar.caption("HIES2026")

# Run Navigation
pg.run()
st.set_page_config(layout="wide")