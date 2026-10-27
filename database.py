import sqlite3
import json

# Name of the local SQLite database
DATABASE_NAME = "jobmatch.db"


# Create the jobs table if it does not already exist
def initialize_database():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                required_skills TEXT,
                url TEXT UNIQUE,
                description TEXT,
                source TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()


# Save live jobs into the database
def save_jobs(jobs):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        for job in jobs:
            # Store the skills list as JSON
            skills_json = json.dumps(
                job.get("required_skills", [])
            )

            cursor.execute("""
                INSERT INTO jobs (
                    title,
                    company,
                    location,
                    required_skills,
                    url,
                    description,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    company = excluded.company,
                    location = excluded.location,
                    required_skills = excluded.required_skills,
                    description = excluded.description,
                    source = excluded.source
            """, (
                job.get("title", "Unknown Title"),
                job.get("company", "Unknown Company"),
                job.get("location", "Unknown Location"),
                skills_json,
                job.get("url", ""),
                job.get("description", ""),
                job.get("source", "Unknown Source"),
            ))

        connection.commit()


# Load saved jobs from SQLite
def load_jobs():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                title,
                company,
                location,
                required_skills,
                url,
                description,
                source
            FROM jobs
        """)

        rows = cursor.fetchall()

    jobs = []

    for row in rows:
        # Restore the skills list from JSON
        try:
            required_skills = json.loads(row[3] or "[]")
        except json.JSONDecodeError:
            required_skills = []

        jobs.append({
            "title": row[0],
            "company": row[1],
            "location": row[2] or "Unknown Location",
            "required_skills": required_skills,
            "url": row[4] or "",
            "description": row[5] or "",
            "source": row[6] or "Unknown Source",
        })

    return jobs


# Count the number of saved jobs
def count_jobs():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM jobs")

        result = cursor.fetchone()

    return result[0]
