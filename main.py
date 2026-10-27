import json
import urllib.request
import urllib.error

# Arbeitnow public job listings API
API_URL = "https://www.arbeitnow.com/api/job-board-api"

# Standardize common skill aliases
SKILL_ALIASES = {
    "js": "javascript",
    "postgres": "postgresql",
}


# Normalize skill names for consistent matching
def normalize_skill(skill):
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)


# Fetch live jobs from the API
def fetch_jobs_from_api():
    try:
        # Send a request to the API
        request = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "JobMatch/1.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Extract the job listings from the response
        api_jobs = data.get("data", [])

        jobs = []

        # Convert API listings into JobMatch's data structure
        for item in api_jobs:
            tags = item.get("tags", [])

            # Normalize tags so they can be used as required skills
            required_skills = list(dict.fromkeys(
                normalize_skill(tag)
                for tag in tags
                if isinstance(tag, str)
            ))

            # Create a job object using the API information
            job = {
                "title": item.get("title", "Unknown Title"),
                "company": item.get("company_name", "Unknown Company"),
                "required_skills": required_skills,
                "location": item.get("location", "Unknown Location"),
                "url": item.get("url", ""),
                "source": "Arbeitnow API",
            }

            jobs.append(job)

        return jobs

    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print("Could not connect to the job API:", error)
        return []


# Load sample jobs from the local JSON file
def load_sample_jobs():
    try:
        with open("jobs.json", "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Error: jobs.json was not found.")
        return []

    except json.JSONDecodeError:
        print("Error: jobs.json contains invalid JSON.")
        return []


# Calculate how well a user's skills match a job
def calculate_match(my_skills, required_skills):
    # Normalize the user's skills
    normalized_my_skills = {
        normalize_skill(skill)
        for skill in my_skills
    }

    matched_skills = []
    missing_skills = []

    # Compare user skills with required skills
    for skill in required_skills:
        normalized_required = normalize_skill(skill)

        if normalized_required in normalized_my_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Avoid division by zero
    if not required_skills:
        return matched_skills, missing_skills, 0

    # Calculate the percentage of skills matched
    percentage = (
        len(matched_skills) / len(required_skills)
    ) * 100

    return matched_skills, missing_skills, percentage


# Search jobs by title or required skills
def search_jobs(jobs, keyword):
    keyword = normalize_skill(keyword)

    # Return every job when no keyword is provided
    if not keyword:
        return jobs

    matching_jobs = []

    # Check each job for a keyword match
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


# Filter jobs by minimum match percentage
def filter_jobs(jobs, minimum):
    filtered = []

    # Keep jobs that meet the minimum percentage
    for job in jobs:
        if job["match_percentage"] >= minimum:
            filtered.append(job)

    return filtered


# Main application function
def main():
    print("\n=== JOBMATCH ===")
    print("Loading job listings...")

    # Try to retrieve live jobs from the API
    jobs = fetch_jobs_from_api()

    # Use local sample data if the API is unavailable
    if jobs:
        print("Loaded", len(jobs), "jobs from Arbeitnow API.")
    else:
        print("Using local sample job listings.")
        jobs = load_sample_jobs()

    # Stop if no jobs could be loaded
    if not jobs:
        print("No job listings are available.")
        return

    # Ask the user to enter their skills
    user_input = input(
        "\nEnter your skills, separated by commas or spaces: "
    )

    # Normalize skills and remove duplicates
    my_skills = list(dict.fromkeys(
        normalize_skill(skill)
        for skill in user_input.replace(",", " ").split()
        if skill.strip()
    ))

    # Ensure the user entered at least one skill
    if not my_skills:
        print("Please enter at least one skill.")
        return

    # Ask for a search keyword
    keyword = input(
        "Search jobs by title or skill "
        "(press Enter for all jobs): "
    )

    # Search the available job listings
    matching_jobs = search_jobs(jobs, keyword)

    if not matching_jobs:
        print("No jobs found matching your search.")
        return

    # Calculate match details for every job
    for job in matching_jobs:
        matched, missing, percentage = calculate_match(
            my_skills,
            job["required_skills"]
        )

        job["matched_skills"] = matched
        job["missing_skills"] = missing
        job["match_percentage"] = percentage

    # Ask for the minimum match percentage
    minimum_input = input(
        "Minimum match percentage (0-100, default 0): "
    )

    # Use zero when the user presses Enter
    if minimum_input.strip() == "":
        minimum = 0

    else:
        # Convert input to a number
        try:
            minimum = float(minimum_input)

        except ValueError:
            print("Please enter a valid number.")
            return

        # Validate the percentage range
        if minimum < 0 or minimum > 100:
            print("Enter a percentage between 0 and 100.")
            return

    # Filter jobs using the minimum percentage
    matching_jobs = filter_jobs(matching_jobs, minimum)

    if not matching_jobs:
        print("No jobs meet your minimum match percentage.")
        return

    # Sort jobs from highest to lowest match
    matching_jobs.sort(
        key=lambda job: job["match_percentage"],
        reverse=True
    )

    # Display the results
    print("\n=== JOBMATCH RESULTS ===")

    for job in matching_jobs:
        print("\nJob:", job["title"])
        print("Company:", job["company"])
        print("Location:", job.get("location", "Unknown"))
        print("Matched skills:", job["matched_skills"])
        print("Missing skills:", job["missing_skills"])
        print(
            "Match:",
            round(job["match_percentage"], 1),
            "%"
        )

        # Display the application link when available
        if job.get("url"):
            print("Apply:", job["url"])


# Run the program when this file is executed directly
if __name__ == "__main__":
    main()