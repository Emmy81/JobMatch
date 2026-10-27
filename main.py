import json
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser

from database import (
    initialize_database,
    save_jobs,
    load_jobs,
    count_jobs,
)


# Arbeitnow public job listings API
API_URL = "https://www.arbeitnow.com/api/job-board-api"


# Standardize common skill aliases
SKILL_ALIASES = {
    "js": "javascript",
    "postgres": "postgresql",
    "py": "python",
}


# Known technical skills JobMatch can recognize
KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "php",
    "go",
    "golang",
    "rust",
    "ruby",
    "swift",
    "kotlin",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "express",
    "django",
    "flask",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "sqlite",
    "git",
    "github",
    "docker",
    "kubernetes",
    "linux",
    "aws",
    "azure",
    "google cloud",
    "rest api",
    "graphql",
    "machine learning",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "figma",
    "agile",
    "scrum",
]


# Remove HTML markup from job descriptions
class HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return " ".join(self.text_parts)


# Convert HTML descriptions into readable text
def strip_html(html_text):
    parser = HTMLTextParser()
    parser.feed(html_text or "")
    return parser.get_text()


# Normalize skill names
def normalize_skill(skill):
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)


# Extract recognized technical skills from text
def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in KNOWN_SKILLS:
        # Match the complete skill name
        # This prevents Java from matching JavaScript
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            normalized = normalize_skill(skill)

            if normalized not in found_skills:
                found_skills.append(normalized)

    return found_skills


# Fetch live job listings from Arbeitnow
def fetch_jobs_from_api():
    try:
        request = urllib.request.Request(
            API_URL,
            headers={
                "User-Agent": "JobMatch/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        api_jobs = data.get("data", [])

        jobs = []

        for item in api_jobs:
            # Get the job tags
            tags = item.get("tags", [])

            # Convert tags into text
            tag_text = " ".join(
                tag for tag in tags
                if isinstance(tag, str)
            )

            # Extract the job description
            description = strip_html(
                item.get("description", "")
            )

            # Identify technical skills in both sources
            tag_skills = extract_skills(tag_text)
            description_skills = extract_skills(description)

            # Combine skills without duplicates
            required_skills = list(dict.fromkeys(
                tag_skills + description_skills
            ))

            # Build the JobMatch job structure
            job = {
                "title": item.get(
                    "title",
                    "Unknown Title"
                ),
                "company": item.get(
                    "company_name",
                    "Unknown Company"
                ),
                "required_skills": required_skills,
                "location": item.get(
                    "location",
                    "Unknown Location"
                ),
                "url": item.get("url", ""),
                "description": description,
                "source": "Arbeitnow API",
            }

            jobs.append(job)

        return jobs

    except (
        urllib.error.URLError,
        TimeoutError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:

        print(
            "Could not retrieve jobs from the API:",
            error
        )

        return []


# Load sample jobs from jobs.json
def load_sample_jobs():
    try:
        with open(
            "jobs.json",
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:
        print("Error: jobs.json was not found.")
        return []

    except json.JSONDecodeError:
        print("Error: jobs.json contains invalid JSON.")
        return []


# Calculate how well a user's skills match a job
def calculate_match(my_skills, required_skills):
    normalized_my_skills = {
        normalize_skill(skill)
        for skill in my_skills
    }

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        normalized_required = normalize_skill(skill)

        if normalized_required in normalized_my_skills:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    # Avoid division by zero
    if not required_skills:
        return matched_skills, missing_skills, 0

    percentage = (
        len(matched_skills) / len(required_skills)
    ) * 100

    return matched_skills, missing_skills, percentage


# Search jobs by title or recognized skill
def search_jobs(jobs, keyword):
    keyword = normalize_skill(keyword)

    # Empty search returns all jobs
    if not keyword:
        return jobs

    matching_jobs = []

    for job in jobs:
        title = job.get("title", "").lower()

        skills = [
            normalize_skill(skill)
            for skill in job.get(
                "required_skills",
                []
            )
        ]

        # Search the title and extracted skills
        if (
            keyword in title
            or any(
                keyword in skill
                for skill in skills
            )
        ):
            matching_jobs.append(job)

    return matching_jobs


# Filter jobs by minimum match percentage
def filter_jobs(jobs, minimum):
    return [
        job for job in jobs
        if job["match_percentage"] >= minimum
    ]


# Main application function
def main():
    print("\n=== JOBMATCH ===")

    # Prepare the SQLite database
    initialize_database()

    print("Loading job listings...")

    # Try to fetch fresh jobs from the API
    jobs = fetch_jobs_from_api()

    if jobs:
        print(
            "Loaded",
            len(jobs),
            "jobs from Arbeitnow API."
        )

        # Save live jobs to SQLite
        save_jobs(jobs)

        print(
            "Saved jobs to SQLite:",
            count_jobs()
        )

    else:
        print(
            "API unavailable. Loading saved jobs."
        )

        # Use previously saved jobs
        jobs = load_jobs()

        # Fall back to sample data if necessary
        if not jobs:
            print(
                "No saved jobs found. "
                "Using sample listings."
            )

            jobs = load_sample_jobs()

    # Stop if no listings are available
    if not jobs:
        print("No job listings are available.")
        return

    # Ask the user for their skills
    user_input = input(
        "\nEnter your skills, "
        "separated by commas or spaces: "
    )

    my_skills = list(dict.fromkeys(
        normalize_skill(skill)
        for skill in user_input.replace(
            ",",
            " "
        ).split()
        if skill.strip()
    ))

    if not my_skills:
        print("Please enter at least one skill.")
        return

    # Ask for a search keyword
    keyword = input(
        "Search jobs by title or skill "
        "(press Enter for all jobs): "
    )

    # Search available jobs
    matching_jobs = search_jobs(
        jobs,
        keyword
    )

    if not matching_jobs:
        print(
            "No jobs found matching your search."
        )
        return

    # Calculate match scores
    for job in matching_jobs:
        matched, missing, percentage = calculate_match(
            my_skills,
            job.get("required_skills", [])
        )

        job["matched_skills"] = matched
        job["missing_skills"] = missing
        job["match_percentage"] = percentage

    # Ask for the minimum match percentage
    minimum_input = input(
        "Minimum match percentage "
        "(0-100, default 0): "
    )

    if minimum_input.strip() == "":
        minimum = 0

    else:
        try:
            minimum = float(minimum_input)

        except ValueError:
            print("Please enter a valid number.")
            return

        if minimum < 0 or minimum > 100:
            print(
                "Enter a percentage between 0 and 100."
            )
            return

    # Filter by minimum score
    matching_jobs = filter_jobs(
        matching_jobs,
        minimum
    )

    if not matching_jobs:
        print(
            "No jobs meet your minimum "
            "match percentage."
        )
        return

    # Sort by highest match first
    matching_jobs.sort(
        key=lambda job: job["match_percentage"],
        reverse=True
    )

    # Display results
    print("\n=== JOBMATCH RESULTS ===")

    for job in matching_jobs:
        print("\nJob:", job["title"])
        print("Company:", job["company"])

        print(
            "Location:",
            job.get(
                "location",
                "Unknown"
            )
        )

        print(
            "Matched skills:",
            job["matched_skills"]
        )

        print(
            "Missing skills:",
            job["missing_skills"]
        )

        print(
            "Match:",
            round(
                job["match_percentage"],
                1
            ),
            "%"
        )

        # Explain when no skills were detected
        if not job.get("required_skills"):
            print(
                "Note: No recognized technical "
                "skills were detected."
            )

        # Display the application URL
        if job.get("url"):
            print(
                "Apply:",
                job["url"]
            )


# Run the application
if __name__ == "__main__":
    main()
