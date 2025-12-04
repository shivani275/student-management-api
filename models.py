from sqlalchemy import Column, Integer, String, Float, LargeBinary, DateTime
from datetime import datetime
import base64
from database import Base
# models.py
# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize Flask-SQLAlchemy

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(100), nullable=False)

    math = db.Column(db.Float, default=0.0)
    science = db.Column(db.Float, default=0.0)
    english = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(2), nullable=True)
    attendance = db.Column(db.Float, default=100.0)
    photo = db.Column(db.LargeBinary, nullable=True)

    def compute_total_and_grade(self):
        self.total = (self.math or 0) + (self.science or 0) + (self.english or 0)
        avg = self.total / 3
        if avg >= 90:
            self.grade = "A+"
        elif avg >= 80:
            self.grade = "A"
        elif avg >= 70:
            self.grade = "B+"
        elif avg >= 60:
            self.grade = "B"
        elif avg >= 50:
            self.grade = "C"
        else:
            self.grade = "F"
        return self.total, self.grade


    # ----------------------------------------------------------------------
    # Convert photo to Base64 safely
    # ----------------------------------------------------------------------
    def photo_base64(self):
        """Return base64 string of stored photo. Returns empty string if no photo."""
        if not self.photo:
            return ""
        try:
            if isinstance(self.photo, (bytes, bytearray)):
                return base64.b64encode(self.photo).decode("utf-8")
            # If photo is accidentally stored as string
            elif isinstance(self.photo, str):
                return base64.b64encode(self.photo.encode("utf-8")).decode("utf-8")
            else:
                return ""
        except Exception:
            return ""
