from typing import Dict, List
from database import Base

def predict_grade(avg: float) -> str:
    if avg >= 90:
        return "A+"
    elif avg >= 80:
        return "A"
    elif avg >= 70:
        return "B+"
    elif avg >= 60:
        return "B"
    elif avg >= 50:
        return "C"
    else:
        return "F"

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0

def ai_insights(math: float, science: float, english: float, attendance: float) -> Dict:
    """
    Generate AI-style insights based on subject performance and attendance.
    Handles None/empty values safely.
    """

    # Convert safely using safe_float
    math = safe_float(math)
    science = safe_float(science)
    english = safe_float(english)
    attendance = safe_float(attendance)

    # Compute average safely
    avg = round((math + science + english) / 3, 2)
    grade = predict_grade(avg)

    # Identify weak subjects
    subjects = {
        "Math": math,
        "Science": science,
        "English": english
    }
    weak_subjects: List[str] = [subj for subj, score in subjects.items() if score < avg]

    # Generate suggestions
    suggestions: List[str] = []

    if "Math" in weak_subjects:
        suggestions.append("Practice topic-wise Math problems and revise formulas.")
    if "Science" in weak_subjects:
        suggestions.append("Revise Science fundamentals and perform simple experiments.")
    if "English" in weak_subjects:
        suggestions.append("Improve vocabulary and practice comprehension passages.")

    if attendance < 75:
        suggestions.append("Attend classes regularly to improve learning consistency.")

    if not suggestions:
        suggestions.append("Great performance! Continue with regular revision and mock tests.")

    return {
        "avg": avg,
        "grade": grade,
        "weak_subjects": weak_subjects,
        "suggestions": suggestions
    }
