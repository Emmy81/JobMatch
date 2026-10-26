my_skills = ["Python", "Git", "HTML"]
required_skills = ["Python", "Git", "SQL", "Django"]

# Store the skills that match
matched_skills = []

# Check each skill required by the job
for skill in required_skills:
    if skill in my_skills:
        matched_skills.append(skill)

# Count the matched skills and required skills
matched_count = len(matched_skills)
required_count = len(required_skills)

# Calculate the job match percentage
match_percentage = (matched_count / required_count) * 100

# Display the results
print("Matched skills:", matched_skills)
print("Number of matched skills:", matched_count)
print("Total required skills:", required_count)
print("Job match:", match_percentage, "%")
