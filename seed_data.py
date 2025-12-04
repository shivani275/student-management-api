# seed_data.py
import os
from database import engine
import models
from sqlalchemy.orm import Session
from datetime import datetime

# -------------------------------
# Delete old DB (development only)
# -------------------------------
DB_FILE = "students.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Deleted old database {DB_FILE}")

# -------------------------------
# Create tables
# -------------------------------
models.Base.metadata.create_all(bind=engine)

# -------------------------------
# Sample data
# -------------------------------
samples = [
    {"name":"Alice", "email":"alice@example.com", "course":"Physics", "math":85, "science":90, "english":78, "attendance":95},
    {"name":"Bob", "email":"bob@example.com", "course":"Chemistry", "math":72, "science":65, "english":70, "attendance":88},
    {"name":"Carol", "email":"carol@example.com", "course":"Maths", "math":92, "science":88, "english":90, "attendance":98},
    {"name":"David", "email":"david@example.com", "course":"Physics", "math":60, "science":55, "english":58, "attendance":80},
    {"name":"Eve", "email":"eve@example.com", "course":"Chemistry", "math":78, "science":82, "english":75, "attendance":85},
]

# -------------------------------
# Insert data
# -------------------------------
with Session(engine) as db:
    for s in samples:
        student = models.Student(
            name=s["name"],
            email=s["email"],
            course=s["course"],
            math=s["math"],
            science=s["science"],
            english=s["english"],
            attendance=s["attendance"]
        )
        student.compute_total_and_grade()  # calculates total & grade
        db.add(student)
    db.commit()

print("✅ Seed data created successfully.")
print("Run `uvicorn main:app --reload` and visit /students")
