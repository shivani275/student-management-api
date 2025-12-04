from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud, models, schemas
from database import engine, get_db
from ml_model import predict_grade, ai_insights
from typing import List

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API running"}

# ---------------------- CRUD -------------------------

@app.post("/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):

    s = crud.create_student(db, student)
    out = schemas.StudentOut.model_validate(s).model_dump()
    
    # add base64 image
    out["photo"] = s.photo_base64()
    return out


@app.get("/students", response_model=List[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)):

    students = crud.get_students(db)
    out = []

    for s in students:
        obj = schemas.StudentOut.model_validate(s).model_dump()
        obj["photo"] = s.photo_base64()
        out.append(obj)

    return out


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):

    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")

    obj = schemas.StudentOut.model_validate(s).model_dump()
    obj["photo"] = s.photo_base64()
    return obj


@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, student_in: schemas.StudentCreate, db: Session = Depends(get_db)):

    s = crud.update_student(db, student_id, student_in)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")

    obj = schemas.StudentOut.model_validate(s).model_dump()
    obj["photo"] = s.photo_base64()
    return obj


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):

    ok = crud.delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted"}


# ---------------------- Photo Upload -------------------------

@app.post("/students/{student_id}/photo")
async def upload_photo(student_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")

    contents = await file.read()
    crud.set_student_photo(db, student_id, contents)

    return {"message": "Photo uploaded"}


# ---------------------- Prediction -------------------------

@app.post("/predict-grade")
def predict(payload: dict):

    math = float(payload.get("math", 0))
    science = float(payload.get("science", 0))
    english = float(payload.get("english", 0))

    if "marks" in payload and (math == 0 and science == 0 and english == 0):
        avg = float(payload.get("marks", 0))
        grade = predict_grade(avg)
        insights = ai_insights(avg, avg, avg, payload.get("attendance", 100))
        return {"average": avg, "predicted_grade": grade, "insights": insights}

    avg = (math + science + english) / 3.0
    grade = predict_grade(avg)
    insights = ai_insights(math, science, english, payload.get("attendance", 100))

    return {"average": avg, "predicted_grade": grade, "insights": insights}


# ---------------------- Analytics -------------------------

@app.get("/top-students")
def top_students(limit: int = 5, db: Session = Depends(get_db)):

    students = crud.top_students(db, limit)
    return [
        {
            "id": s.id,
            "name": s.name,
            "course": s.course,
            "total": s.total,
            "grade": s.grade
        }
        for s in students
    ]


@app.get("/course-stats")
def course_stats(db: Session = Depends(get_db)):
    return crud.course_stats(db)


# ---------------------- Run API -------------------------

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
