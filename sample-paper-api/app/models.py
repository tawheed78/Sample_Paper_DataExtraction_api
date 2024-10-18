"""
Models for handling data using Pydantic

This module defines the data models used for validating and serializing 
various fields in the application.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ParamsModel(BaseModel):
    "Model representing parameters for a given board, subject and grade."
    board: Optional[str]= {}
    grade: int
    subject: str

class QuestionsModel(BaseModel):
    "Model representing question with its attributes."
    question: str
    answer: Optional[str] = {}
    type: str
    question_slug: str
    reference_id: Optional[str] = {}
    hint: Optional[str] = {}
    params: Optional[Dict[str, Any]] = {}

class SectionModel(BaseModel):
    "Model representing Section and its attributes."
    marks_per_question: int
    type: str
    questions: List[QuestionsModel]

class PaperModel(BaseModel):
    "Model representing complete PaperModel with its attributes"
    title: str
    type: str
    time: int
    marks: int
    params: Optional[ParamsModel] = {}
    tags: List[str]
    chapters: List[str]
    sections: List[SectionModel]

class TaskStatusModel(BaseModel):
    "Model representing attributes for Task Status."
    task_id: str
    status: str
    description: Optional[str]

class SearchPaperResponseModel(BaseModel):
    "Model representing attributes for Search Paper Model."
    paper_id: str
    title: str
    subject: str

class SearchResponseModel(BaseModel):
    "Model representing attributes to return the response of Search paper endpoint"
    message: str
    results: List[SearchPaperResponseModel]

class TaskStatusResponseModel(BaseModel):
    "Model representing attributes of Task Status response."
    task_id: str
    status: str
    
