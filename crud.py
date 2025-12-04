# crud.py
from sqlalchemy.orm import Session
import models, schemas
from typing import List, Optional


# --------------------------------------
# GET ALL STUDENTS
# --------------------------------------
def get_students(db: Session) -> List[models.Student]:
    return db.query(models.Student).all()


# --------------------------------------
# GET SINGLE STUDENT
# --------------------------------------
def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


# --------------------------------------
# CREATE STUDENT
# --------------------------------------
def create_student(db: Session, student_in: schemas.StudentCreate) -> models.Student:
    # Convert Pydantic → dict
    data = student_in.model_dump()

    # Remove fields that should NOT be set manually
    data.pop("total", None)
    data.pop("grade", None)

    s = models.Student(**data)
    s.compute_total_and_grade()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# --------------------------------------
# UPDATE STUDENT (PARTIAL UPDATE)
# --------------------------------------
def update_student(
    db: Session, 
    student_id: int, 
    student_in: schemas.StudentUpdate
) -> Optional[models.Student]:

    s = get_student(db, student_id)
    if not s:
        return None

    update_data = student_in.model_dump(exclude_unset=True)

    # Do not allow update of total/grade manually
    update_data.pop("total", None)
    update_data.pop("grade", None)

    # Apply only provided fields
    for key, value in update_data.items():
        setattr(s, key, value)

    # Recalculate totals
    s.compute_total_and_grade()

    db.commit()
    db.refresh(s)
    return s


# --------------------------------------
# DELETE STUDENT
# --------------------------------------
def delete_student(db: Session, student_id: int) -> bool:
    s = get_student(db, student_id)
    if not s:
        return False
    db.delete(s)
    db.commit()
    return True


# --------------------------------------
# SET STUDENT PHOTO (BLOB)
# --------------------------------------
def set_student_photo(db: Session, student_id: int, photo_bytes: bytes) -> Optional[models.Student]:
    s = get_student(db, student_id)
    if not s:
        return None
    s.photo = photo_bytes
    db.commit()
    db.refresh(s)
    return s


# --------------------------------------
# TOP STUDENTS
# --------------------------------------
def top_students(db: Session, limit: int = 5):
    return (
        db.query(models.Student)
        .order_by(models.Student.total.desc())
        .limit(limit)
        .all()
    )


# --------------------------------------
# COURSE STATS
# --------------------------------------
def course_stats(db: Session):
    students = get_students(db)
    stats = {}

    for st in students:
        stats.setdefault(st.course, []).append(st.total)

    return {
        course: round(sum(vals) / len(vals), 2)
        for course, vals in stats.items()
    }
