"""
Sample paper routes for ZuAI Sample Paper FastAPI application.

This module defines the API endpoints for extracting data for
sample papers from PDF and Plain Text Input.
"""
import json
import os
import aiofiles
import google.generativeai as genai
from bson import ObjectId
from pydantic import ValidationError
from dotenv import load_dotenv
from pymongo.errors import PyMongoError

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Body, HTTPException,File, Request, UploadFile, BackgroundTasks

from ..rate_limiter import rate_limit
from ..models import PaperModel, TaskStatusResponseModel
from ..config import db, INSTRUCTION, PROMPT, response_schema


load_dotenv()

paper_collection = db['sample_papers']
task_collection = db['task_status']

safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction=INSTRUCTION,
    generation_config={"response_mime_type": "application/json"},
    safety_settings=safe
)

router = APIRouter()

def update_task_status(task_id, status, description=None):
    "Update the status of a background task in the database."
    query = {"_id":ObjectId(task_id)}
    update_data = {"$set": {"status": status}}
    if description:
        update_data["$set"]["description"] = description
    task_collection.update_one(query, update_data)

def generate_sample_paper(sample_pdf, task_id: str):
    "Generate a sample paper using the Generative AI model."
    try:
        response = model.generate_content([PROMPT, sample_pdf])
        if response.parts:
            response_text = response.text
            response = response_text
            return response
    except Exception as e:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=500, detail="Error during content generation") from e

def insert_sample_paper(response: dict, task_id: str):
    "Insert the generated sample paper into the MongoDB collection."
    try:
        sample_paper = PaperModel(**response)
        paper_collection.insert_one(sample_paper.model_dump())
        return True
    except ValidationError as ve:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=422, detail=f"Validation error: {ve}") from ve
    except PyMongoError as pme:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from ve
    except Exception as e:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}") from e

def pdf_extraction_background_task(file_location: str, task_id:str):
    "Background task to process PDF extraction and insert the generated sample paper into the database."
    try:
        sample_pdf = genai.upload_file(file_location)
        response = generate_sample_paper(sample_pdf, task_id)
        if response:
            try:
                response = json.loads(response)
            except json.JSONDecodeError as json_err:
                update_task_status(task_id, status='Failed')
                return {"error": "Invalid JSON response", "detail": str(json_err)}
            result_status = insert_sample_paper(response, task_id)
            if result_status:
                update_task_status(task_id, status='Completed')
                return {"message": "Sample paper extracted and saved successfully"}
    except PyMongoError as pme:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=500, detail="Incorrect response generated. Please try again.") from e

@router.post('/extract/pdf')
@rate_limit(limit=2, time_window=60)
async def extract_pdf(request:Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    "Handle PDF file upload and initiate background task for extraction."
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        file_location = f"data/input/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        try:
            query = {"status": "In Progress"}
            task = await task_collection.insert_one(query)
            task_id = task.inserted_id
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error initializing task") from e
        background_tasks.add_task(pdf_extraction_background_task, file_location, task_id)
        return JSONResponse(status_code=202, content={"message": f"The request for PDF extraction is accepted and is under progress. Please check the task status using Task ID: {task_id}"})
    except Exception as e:
        await update_task_status(task_id, status='Failed')
        raise HTTPException(status_code=500, detail="Operation failed due to internal error.") from e


@router.post('/extract/text')
@rate_limit(limit=3, time_window=60)
async def extract_text(request:Request, input_data: str = Body(...)):
    "Extract and process text input to generate a sample paper using the AI model."
    try:
        if not isinstance(input_data, str):
            raise HTTPException(status_code=400, detail="Only plain text are allowed.")
        response = model.generate_content([PROMPT, input_data])
        response = response.text
        try:
            sample_paper = PaperModel(**json.loads(response))
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Validation error: {ve}") from ve
        paper_collection.insert_one(sample_paper.model_dump())
        return {"message": "Sample paper extracted and saved successfully"}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON response from model.") from exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}") from e

@router.get('/tasks/{task_id}', response_model=TaskStatusResponseModel)
async def task_status(task_id: str):
    "Retrieve the status of a background task by its ID."
    try:
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=400, detail="Invalid Task ID format")
        query = {"_id": ObjectId(task_id)}
        task = await task_collection.find_one(query)
        if not task:
            raise HTTPException(status_code=400, detail="No such Task exists")
        task_status = task.get("status", "Unknown. Please wait as we are looking into the issue...")
        return TaskStatusResponseModel(task_id=task_id, status=task_status)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid input data: {ve}") from ve
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e
