import json

# Standardize common skill aliases
SKILL_ALIASES = {
    "js": "javascript",
    "postgres": "postgresql",
}


def normalize_skill(skill):
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)


# Calculate how well a user matches a job
def calculate_match(my_skills, required_skills):
    normalized_my_skills = {
        normalize_skill(skill)
        for skill in my_skills
    }

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if normalize_skill(skill) in normalized_my_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if not required_skills:
        return matched_skills, missing_skills, 0

    percentage = (
        len(matched_skills) / len(required_skills)
    ) * 100

    return matched_skills, missing_skills, percentage


# Search jobs by title or required skills
def search_jobs(jobs, keyword):
    keyword = keyword.strip().lower()

    if not keyword:
        return jobs

    matching_jobs = []

    for job in jobs:
        title = job["title"].lower()

        skills = [
            normalize_skill(skill)
            for skill in job["required_skills"]
        ]

        if (
            keyword in title
            or any(keyword in skill for skill in skills)
        ):
            matching_jobs.append(job)

    return matching_jobs


def main():
    # Load job listings from jobs.json
    try:
        with open("jobs.json", "r", encoding="utf-8") as file:
            jobs = json.load(file)
    except FileNotFoundError:
        print("Error: jobs.json was not found.")
        print("Place jobs.json in the same folder as main.py.")
        return
    except json.JSONDecodeError:
        print("Error: jobs.json contains invalid JSON.")
        return

    # Collect the user's skills
    user_input = input(
        "Enter your skills, separated by commas or spaces: "
    )

    my_skills = list(dict.fromkeys(
        skill.strip().lower()
        for skill in user_input.replace(",", " ").split()
        if skill.strip()
    ))

    if not my_skills:
        print("Please enter at least one skill.")
        return

    # Ask what jobs the user wants to find
    keyword = input(
        "Search jobs by title or skill "
        "(press Enter for all jobs): "
    )

    filtered_jobs = search_jobs(jobs, keyword)

    if not filtered_jobs:
        print("No jobs found matching your search.")
        return

    # Calculate matches for the filtered jobs
    for job in filtered_jobs:
        matched, missing, percentage = calculate_match(
            my_skills,
            job["required_skills"]
        )

        job["matched_skills"] = matched
        job["missing_skills"] = missing
        job["match_percentage"] = percentage

    # Rank jobs from highest to lowest match
    filtered_jobs.sort(
        key=lambda job: job["match_percentage"],
        reverse=True
    )

    # Display results
    print("\n=== JOBMATCH RESULTS ===")

    for job in filtered_jobs:
        print("\nJob:", job["title"])
        print("Company:", job["company"])
        print("Matched skills:", job["matched_skills"])
        print("Missing skills:", job["missing_skills"])
        print(
            "Match:",
            round(job["match_percentage"], 1),
            "%"
        )


if __name__ == "__main__":
    main()
    
