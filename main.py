
my_skills = ["Python", "Git"]
required_skills = ["Python", "Git", "SQL", "Django"]

matched_skills = []

for skill in required_skills:
    if skill in my_skills:
        matched_skills.append(skill)

print("Matched skills:", matched_skills)
print("Number of matched skills:", len(matched_skills))
