from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ParamsModel(BaseModel):
    board: str
    grade: int
    subject: str

class QuestionsModel(BaseModel):
    question: str
    answer: str
    type: str
    question_slug: str
    reference_id: str
    hint: str
    params: Optional[Dict[str, Any]] = {}

class SectionModel(BaseModel):
    marks_per_question: int
    type: str
    questions: List[QuestionsModel]

class PaperModel(BaseModel):
    title: str
    type: str
    time: int
    marks: int
    params: ParamsModel
    tags: List[str]
    chapters: List[str]
    sections: List[SectionModel]

class Config:
    schema_extra = {
        "example": {
            "title": "Sample Paper Title",
            "type": "previous_year",
            "time": 180,
            "marks": 100,
            "params": {
                "board": "CBSE",
                "grade": 10,
                "subject": "Maths"
            },
            "tags": ["algebra", "geometry"],
            "chapters": ["Quadratic Equations", "Triangles"],
            "sections": [
                {
                    "marks_per_question": 5,
                    "type": "default",
                    "questions": [
                        {
                            "question": "Solve the quadratic equation: x^2 + 5x + 6 = 0",
                            "answer": "The solutions are x = -2 and x = -3",
                            "type": "short",
                            "question_slug": "solve-quadratic-equation",
                            "reference_id": "QE001",
                            "hint": "Use the quadratic formula or factorization method",
                            "params": {}
                        },
                        {
                            "question": "In a right-angled triangle, if one angle is 30°, what is the other acute angle?",
                            "answer": "60°",
                            "type": "short",
                            "question_slug": "right-angle-triangle-angles",
                            "reference_id": "GT001",
                            "hint": "Remember that the sum of angles in a triangle is 180°",
                            "params": {}
                        }
                    ]
                }
            ]
        }
    }