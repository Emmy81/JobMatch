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
    page_title="JobMatch | Find Your Next Role",
    page_icon="🎯",
    layout="wide",
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .jobmatch-subtitle {
        color: #9CA3AF;
        font-size: 1rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    .jobmatch-section {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1rem;
        border-radius: 12px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }

    .skill-label {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .muted-text {
        color: #9CA3AF;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# LOAD SAVED JOBS
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_saved_jobs():
    return load_jobs()


# --------------------------------------------------
# REFRESH LIVE JOBS
# --------------------------------------------------

def refresh_jobs():
    with st.spinner("Retrieving live job listings..."):
        fresh_jobs = fetch_jobs_from_api()

    if fresh_jobs:
        save_jobs(fresh_jobs)
        get_saved_jobs.clear()

        st.success(
            f"Successfully retrieved {len(fresh_jobs)} live listings."
        )

    else:
        st.error(
            "The API request failed. "
            "Your saved listings remain available."
        )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

header_col, refresh_col = st.columns([4, 1])

with header_col:
    st.title("🎯 JobMatch")

    st.markdown(
        '<div class="jobmatch-subtitle">'
        'Discover software engineering opportunities '
        'that align with your skills.'
        '</div>',
        unsafe_allow_html=True,
    )

with refresh_col:
    st.write("")

    if st.button(
        "↻ Refresh Jobs",
        use_container_width=True,
    ):
        refresh_jobs()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("Your Profile")

    st.caption(
        "Tell JobMatch what you know."
    )

    skills_input = st.text_area(
        "Technical skills",
        placeholder=(
            "Python, Git, SQL, Django, "
            "JavaScript, HTML, CSS"
        ),
        height=130,
    )

    st.divider()

    search_keyword = st.text_input(
        "Search jobs",
        placeholder="Python Developer",
    )

    minimum_match = st.slider(
        "Minimum match",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        format="%d%%",
    )

    st.divider()

    st.caption(
        "Job listings are provided by Arbeitnow."
    )


# --------------------------------------------------
# LOAD JOBS
# --------------------------------------------------

jobs = get_saved_jobs()

if not jobs:
    st.warning(
        "No saved job listings were found. "
        "Use Refresh Jobs to retrieve live listings."
    )

    st.stop()


# --------------------------------------------------
# PROCESS USER SKILLS
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
        "Enter your technical skills in the sidebar "
        "to see your matching opportunities."
    )

    st.stop()


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

matching_jobs = search_jobs(
    jobs,
    search_keyword,
)


# --------------------------------------------------
# MATCHING
# --------------------------------------------------

for job in matching_jobs:
    required_skills = job.get(
        "required_skills",
        []
    )

    matched, missing, percentage = calculate_match(
        my_skills,
        required_skills,
    )

    job["matched_skills"] = matched
    job["missing_skills"] = missing
    job["match_percentage"] = percentage


# --------------------------------------------------
# FILTERING
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
result_count = len(matching_jobs)

best_match = (
    matching_jobs[0]["match_percentage"]
    if matching_jobs
    else 0
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "Saved Listings",
        total_jobs,
    )

with metric2:
    st.metric(
        "Matching Results",
        result_count,
    )

with metric3:
    st.metric(
        "Best Match",
        f"{best_match:.1f}%",
    )


# --------------------------------------------------
# RESULTS HEADER
# --------------------------------------------------

st.markdown(
    '<div class="jobmatch-section">'
    'Recommended Opportunities'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Ranked by the percentage of recognized "
    "job skills that match your profile."
)


# --------------------------------------------------
# EMPTY RESULTS
# --------------------------------------------------

if not matching_jobs:
    st.warning(
        "No jobs match your current filters. "
        "Try a different search or lower the "
        "minimum match percentage."
    )

    st.stop()


# --------------------------------------------------
# JOB CARDS
# --------------------------------------------------

for job in matching_jobs:

    with st.container(border=True):

        title_col, score_col = st.columns(
            [4, 1]
        )

        with title_col:
            st.subheader(
                job.get(
                    "title",
                    "Unknown Title",
                )
            )

            st.write(
                f"**{job.get('company', 'Unknown Company')}**"
            )

            st.caption(
                f"📍 {job.get('location', 'Unknown Location')}"
            )

        with score_col:
            st.metric(
                "Skill Match",
                f"{job['match_percentage']:.1f}%",
            )

        st.divider()

        # Matched skills
        st.markdown(
            '<div class="skill-label">'
            'Skills You Match'
            '</div>',
            unsafe_allow_html=True,
        )

        if job["matched_skills"]:
            st.success(
                " · ".join(job["matched_skills"])
            )

        else:
            st.write(
                "No recognized skills matched."
            )

        # Missing skills
        st.markdown(
            '<div class="skill-label">'
            'Skills to Develop'
            '</div>',
            unsafe_allow_html=True,
        )

        if job["missing_skills"]:
            st.warning(
                " · ".join(job["missing_skills"])
            )

        elif job.get("required_skills"):
            st.success(
                "All recognized skills matched."
            )

        else:
            st.info(
                "No recognized technical skills "
                "were detected in this listing. "
                "The score may not be meaningful."
            )

        # Job description
        description = job.get(
            "description",
            "",
        )

        if description:
            with st.expander(
                "Read job description"
            ):
                st.write(description)

        # Application link
        job_url = job.get(
            "url",
            "",
        )

        if job_url:
            st.link_button(
                "View Job & Apply ↗",
                job_url,
                use_container_width=True,
            )

        st.caption(
            f"Source: {job.get('source', 'Unknown')}"
        )
