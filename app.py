import streamlit as st

from main import (
    fetch_jobs_from_api,
    calculate_match,
    normalize_skill,
    search_jobs,
)

from database import (
    initialize_database,
    save_jobs,
    load_jobs,
    count_jobs,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="JobMatch",
    page_icon="🎯",
    layout="wide",
)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# LOAD JOBS
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_saved_jobs():
    return load_jobs()


def refresh_jobs():
    # Retrieve fresh listings from Arbeitnow
    with st.spinner("Fetching live jobs from Arbeitnow..."):
        jobs = fetch_jobs_from_api()

    if jobs:
        # Save retrieved jobs into SQLite
        save_jobs(jobs)

        # Clear cached database results
        get_saved_jobs.clear()

        st.success(
            f"Successfully refreshed {len(jobs)} job listings."
        )

    else:
        st.error(
            "Could not retrieve live jobs. "
            "Your saved listings are still available."
        )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🎯 JobMatch")

st.write(
    "Find software engineering jobs that match "
    "your skills and experience."
)

st.caption(
    "Live job listings powered by Arbeitnow "
    "with skill-based matching."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("Your Profile")

    skills_input = st.text_area(
        "Your technical skills",
        placeholder=(
            "Python, Git, SQL, Django, "
            "JavaScript, HTML, CSS"
        ),
        help=(
            "Enter your skills separated by commas."
        ),
        height=120,
    )

    search_keyword = st.text_input(
        "Search job titles or skills",
        placeholder="e.g. Python Developer",
    )

    minimum_match = st.slider(
        "Minimum match percentage",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

    st.divider()

    refresh_button = st.button(
        "Refresh Live Jobs",
        use_container_width=True,
    )

    st.caption(
        "Refresh retrieves the latest available "
        "listings from Arbeitnow."
    )


# --------------------------------------------------
# REFRESH JOBS
# --------------------------------------------------

if refresh_button:
    refresh_jobs()


# --------------------------------------------------
# LOAD DATABASE JOBS
# --------------------------------------------------

jobs = get_saved_jobs()

if not jobs:
    st.warning(
        "No saved jobs are available yet. "
        "Use the Refresh Live Jobs button to retrieve listings."
    )

    st.stop()


# --------------------------------------------------
# PROFILE VALIDATION
# --------------------------------------------------

my_skills = list(dict.fromkeys(
    normalize_skill(skill)
    for skill in skills_input.replace(
        ",",
        " "
    ).split()
    if skill.strip()
))

if not my_skills:
    st.info(
        "Enter your skills in the sidebar "
        "to begin finding matching jobs."
    )

    st.stop()


# --------------------------------------------------
# SEARCH JOBS
# --------------------------------------------------

matching_jobs = search_jobs(
    jobs,
    search_keyword,
)


# --------------------------------------------------
# CALCULATE MATCH SCORES
# --------------------------------------------------

for job in matching_jobs:
    matched, missing, percentage = calculate_match(
        my_skills,
        job.get("required_skills", [])
    )

    job["matched_skills"] = matched
    job["missing_skills"] = missing
    job["match_percentage"] = percentage


# --------------------------------------------------
# FILTER AND SORT
# --------------------------------------------------

matching_jobs = [
    job for job in matching_jobs
    if job["match_percentage"] >= minimum_match
]

matching_jobs.sort(
    key=lambda job: job["match_percentage"],
    reverse=True,
)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

total_jobs = len(jobs)
matching_count = len(matching_jobs)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Saved Job Listings",
        total_jobs,
    )

with col2:
    st.metric(
        "Matching Jobs",
        matching_count,
    )

with col3:
    if matching_jobs:
        best_match = matching_jobs[0]["match_percentage"]
    else:
        best_match = 0

    st.metric(
        "Best Match",
        f"{best_match:.1f}%",
    )


st.divider()


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

st.subheader("Recommended Jobs")

if not matching_jobs:
    st.warning(
        "No jobs match your current filters. "
        "Try lowering the minimum match percentage "
        "or changing your search."
    )

    st.stop()


st.write(
    f"Showing {len(matching_jobs)} matching job listings."
)


# --------------------------------------------------
# JOB CARDS
# --------------------------------------------------

for index, job in enumerate(matching_jobs):
    with st.container(border=True):

        # Job title and match score
        title_col, score_col = st.columns(
            [4, 1]
        )

        with title_col:
            st.subheader(
                job.get(
                    "title",
                    "Unknown Title"
                )
            )

            st.write(
                job.get(
                    "company",
                    "Unknown Company"
                )
            )

            st.caption(
                job.get(
                    "location",
                    "Unknown Location"
                )
            )

        with score_col:
            st.metric(
                "Match",
                f"{job['match_percentage']:.1f}%",
            )

        # Display matched skills
        st.markdown("**Matched Skills**")

        if job["matched_skills"]:
            st.success(
                ", ".join(job["matched_skills"])
            )

        else:
            st.write(
                "No recognized skills matched."
            )

        # Display missing skills
        st.markdown("**Skills to Develop**")

        if job["missing_skills"]:
            st.warning(
                ", ".join(job["missing_skills"])
            )

        else:
            st.success(
                "All recognized required skills matched."
            )

        # Expandable job description
        description = job.get(
            "description",
            ""
        )

        if description:
            with st.expander(
                "View Job Description"
            ):
                st.write(description)

        # Application link
        job_url = job.get("url", "")

        if job_url:
            st.link_button(
                "Apply for this Job",
                job_url,
                use_container_width=True,
            )

        st.caption(
            f"Source: {job.get('source', 'Unknown')}"
        )
