# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Student

# Uncomment if you have these ML functions
# from ml_model import predict_grade, ai_insights

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except (ValueError, TypeError):
        return default

# -----------------------------
# ERROR HANDLER
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400


# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Smart Student Performance Management System API is running!"})


# -----------------------------
# CREATE STUDENT
# -----------------------------
@app.route("/students", methods=["POST"])
def add_student():
    if not request.is_json:
        return jsonify({"error": "Expected JSON body"}), 400
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    course = data.get("course")
    if not name or not email or not course:
        return jsonify({"error": "Missing required fields: name, email, course"}), 400

    math = safe_float(data.get("math"), 0.0)
    science = safe_float(data.get("science"), 0.0)
    english = safe_float(data.get("english"), 0.0)
    attendance = safe_float(data.get("attendance"), 100.0)

    existing = Student.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already exists"}), 400

    try:
        student = Student(
            name=name,
            email=email,
            course=course,
            math=math,
            science=science,
            english=english,
            attendance=attendance,
        )
        student.compute_total_and_grade()
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student added successfully", "id": student.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add student", "detail": str(e)}), 500


# -----------------------------
# READ ALL STUDENTS
# -----------------------------
@app.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    out = []
    for s in students:
        out.append(
            {
                "id": s.id,
                "name": s.name,
                "email": s.email,
                "course": s.course,
                "math": s.math,
                "science": s.science,
                "english": s.english,
                "total": s.total,
                "grade": s.grade,
                "attendance": s.attendance,
            }
        )
    return jsonify(out), 200


# -----------------------------
# READ SINGLE STUDENT
# -----------------------------
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    s = Student.query.get_or_404(id)
    return jsonify({
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "course": s.course,
        "math": s.math,
        "science": s.science,
        "english": s.english,
        "total": s.total,
        "grade": s.grade,
        "attendance": s.attendance,
    }), 200

# -----------------------------
# UPDATE STUDENT
# -----------------------------
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    s = Student.query.get_or_404(id)
    if not request.is_json:
        return jsonify({"error": "Expected JSON body"}), 400
    data = request.get_json()
    s.name = data.get("name", s.name)
    s.email = data.get("email", s.email)
    s.course = data.get("course", s.course)
    s.math = safe_float(data.get("math"), s.math)
    s.science = safe_float(data.get("science"), s.science)
    s.english = safe_float(data.get("english"), s.english)
    s.attendance = safe_float(data.get("attendance"), s.attendance)
    try:
        s.compute_total_and_grade()
        db.session.commit()
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update", "detail": str(e)}), 500

# -----------------------------
# DELETE STUDENT
# -----------------------------
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    s = Student.query.get_or_404(id)
    try:
        db.session.delete(s)
        db.session.commit()
        return jsonify({"message": "Student deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete", "detail": str(e)}), 50


# -----------------------------
# ML GRADE PREDICTION
# -----------------------------
@app.route("/predict-grade", methods=["POST"])
def grade_prediction():
    if not request.is_json:
        return jsonify({"error": "Expected JSON body"}), 400
    data = request.get_json()
    # accept either math/science/english or marks(avg)
    math = safe_float(data.get("math"), 0.0)
    science = safe_float(data.get("science"), 0.0)
    english = safe_float(data.get("english"), 0.0)

    if all(v == 0.0 for v in (math, science, english)) and "marks" in data:
        avg = safe_float(data.get("marks"), 0.0)
        grade = predict_grade(avg)
        insights = ai_insights(avg, avg, avg, safe_float(data.get("attendance"), 100.0))
    else:
        avg = (math + science + english) / 3.0
        grade = predict_grade(avg)
        insights = ai_insights(math, science, english, safe_float(data.get("attendance"), 100.0))

    return jsonify({"average": round(avg, 2), "predicted_grade": grade, "insights": insights}), 200


# -----------------------------
# TOP 5 STUDENTS
# -----------------------------
@app.route("/top-students", methods=["GET"])
def top_students():
    students = Student.query.order_by(Student.total.desc()).limit(5).all()
    return (
        jsonify(
            [
                {"name": s.name, "course": s.course, "total": s.total, "grade": s.grade}
                for s in students
            ]
        ),
        200,
    )


# -----------------------------
# COURSE STATISTICS (AVG MARKS)
# -----------------------------
@app.route("/course-stats", methods=["GET"])
def course_stats():
    students = Student.query.all()
    stats = {}
    for s in students:
        stats.setdefault(s.course, []).append(s.total)
    result = {course: round(sum(totals) / len(totals), 2) for course, totals in stats.items()}
    return jsonify(result), 200


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
