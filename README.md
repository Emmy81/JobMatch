JobMatch

JobMatch is a beginner-friendly Python project that compares your skills with sample job listings, identifies skill gaps, and ranks jobs by match percentage.

The project is being built incrementally to practise Python programming and explore how job-matching tools work.

Features

- Enter skills separated by commas or spaces.
- Search job listings by title or required skill.
- Match user skills against job requirements.
- Display matched and missing skills.
- Calculate a match percentage for each listing.
- Rank results from highest to lowest match.
- Load job data from a JSON file.
- Normalize common skill aliases such as "JS" and "JavaScript".

Project structure

JobMatch/
├── main.py
├── jobs.json
└── README.md

- "main.py" contains the application logic.
- "jobs.json" contains the sample job listings.
- "README.md" documents the project.

Requirements

- Python 3.10 or newer recommended.
- No third-party packages are currently required.

How to run

Keep "main.py" and "jobs.json" in the same directory.

Run the program from your terminal:

python main.py

Enter your skills when prompted, for example:

python, git, sql

Then enter a job title or skill to search for, such as "backend" or "SQL". Press Enter without a search term to view all sample listings.

Sample data

The current dataset contains illustrative Python, frontend, and backend developer roles.

These are sample listings, not live vacancies. The project does not currently connect to a real job-search service.

Current limitations

- Job listings are stored locally in "jobs.json".
- Only a small number of skill aliases are supported.
- Match percentages reflect required skills in the dataset and do not guarantee job suitability.

Roadmap

- Improve skill normalization and search accuracy.
- Add automated tests.
- Improve the results display.
- Connect to a suitable job listings API.
- Add more useful job details and filtering options.

Learning objectives

JobMatch is a practical project for learning Python functions, lists, dictionaries, JSON file handling, input validation, searching, sorting, and eventually API integration.

---

Built by "Emmy81" (https://github.com/Emmy81).
