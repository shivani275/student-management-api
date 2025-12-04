from pydantic import BaseModel
from typing import Optional

# ---------------------- Base Schema ----------------------
class StudentBase(BaseModel):
    name: str
    course: str
    math: float
    science: float
    english: float
    attendance: float

# ---------------------- Create Schema ----------------------
class StudentCreate(StudentBase):
    pass

# ---------------------- Update Schema ----------------------
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    course: Optional[str] = None
    math: Optional[float] = None
    science: Optional[float] = None
    english: Optional[float] = None
    attendance: Optional[float] = None

# ---------------------- Output Schema ----------------------
class StudentOut(StudentBase):
    id: int
    total: float
    grade: str
    photo: Optional[str] = None  # base64 image string

    # Pydantic v2: enable from_orm-style parsing
    model_config = {
        "from_attributes": True
    }
