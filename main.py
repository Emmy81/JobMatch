user_input = input("Enter your skills, separated by commas or spaces: ")

my_skills = user_input.lower().replace(",", " ").split()
if not my_skills:
    print("Please enter at least one skill.")
    exit()
    
jobs = [
    {
        "title": "Python Developer",
        "company": "Tech A",
        "required_skills": ["Python", "Git", "SQL"]
    },
    {
        "title": "Frontend Developer",
        "company": "Tech B",
        "required_skills": ["Python", "HTML", "CSS"]
    },
    {
        "title": "Backend Developer",
        "company": "Tech C",
        "required_skills": ["Python", "Django", "SQL", "Git"]
    }
]


def calculate_match(my_skills, required_skills):
    matched_skills = []

    for skill in required_skills:
        if skill.lower() in my_skills:
            matched_skills.append(skill)

    if len(required_skills) == 0:
        return matched_skills, 0

    percentage = len(matched_skills) / len(required_skills) * 100

    return matched_skills, percentage


for job in jobs:
    matched, percentage = calculate_match(
        my_skills, job["required_skills"]
    )

    job["matched_skills"] = matched
    job["match_percentage"] = percentage


jobs.sort(
    key=lambda job: job["match_percentage"],
    reverse=True
)

# Display the results
print("=== JOBMATCH RESULTS ===")

for job in jobs:
    print("\nJob:", job["title"])
    print("Company:", job["company"])
    print("Matched skills:", job["matched_skills"])
    print("Match:", round(job["match_percentage"], 1), "%")
    
