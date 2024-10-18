import json, os, aiofiles
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from ..models import PaperModel
from ..config import db, instruction, prompt
from fastapi import APIRouter, Body, HTTPException,File, Request, UploadFile
import google.generativeai as genai
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from app.rate_limiter import rate_limit

load_dotenv()

paper_collection = db['sample_papers']
task_collection = db['task_status']

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction=instruction,
    generation_config={"response_mime_type": "application/json"}
)

router = APIRouter()


async def generate_sample_paper(sample_pdf, task_id: str):
    try:
        response = model.generate_content([prompt, sample_pdf,])  
        response = jsonable_encoder(response.text)
        response =json.loads(response)
        return response
    
    except json.JSONDecodeError as e:
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=500, detail="Invalid response from content generation")
    
    except Exception as e:
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=500, detail="Error during content generation")

async def insert_sample_paper(response: dict, task_id: str):
    try:
        sample_paper = PaperModel(**response) 
        await paper_collection.insert_one(sample_paper.model_dump())
    
    except ValidationError as ve:
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
    
    except PyMongoError as pme:
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    
    except Exception as e:
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


@router.post('/extract/pdf')
@rate_limit(limit=2, time_window=60) 
async def extract_pdf(request:Request, file: UploadFile = File(...)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
        file_location = f"data/input/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

        try:
            async with aiofiles.open(file_location, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
        except OSError as e:
            raise HTTPException(status_code=500, detail="Error while reading/writing file to disk")
        
        try:
            task = await task_collection.insert_one({"status": "In Progress"})
            task_id = task.inserted_id
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error initializing task")
        
        try:
            sample_pdf = genai.upload_file(file_location)
        except Exception as e:
            await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
            raise HTTPException(status_code=500, detail="Error Uploading PDF")
        
        response = await generate_sample_paper(sample_pdf, task_id)
        # try:
        #     response = await generate_sample_paper(sample_pdf)
        # except Exception as e:
        #     await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed", "description": e}})
        #     raise HTTPException(status_code=500, detail="Error generating response")
        await insert_sample_paper(response, task_id)
        # try:
        #     await insert_sample_paper(response)
        # except Exception as e:
        #     task = await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed", "description": e}})
        #     raise HTTPException(status_code=500, detail="An internal server error occured")
        
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Completed"}})
        return {"message": "Sample paper extracted and saved successfully"}
    except Exception as e:
        print(e)
        await task_collection.update_one({"_id":ObjectId(task_id)},{"$set": {"status": "Failed"}})
        raise HTTPException(status_code=500, detail="Operation failed due to internal error.")


@router.post('/extract/text')
@rate_limit(limit=3, time_window=60) 
async def extract_text(request:Request, input_data: str = Body(...)):
    try:
        if not isinstance(input_data, str):
            raise HTTPException(status_code=400, detail="Only plain text are allowed.")
        response = model.generate_content([prompt, input_data])
        response = response.text
        try:
            sample_paper = PaperModel(**json.loads(response))
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
        result = paper_collection.insert_one(sample_paper.model_dump())
        return {"message": "Sample paper extracted and saved successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON response from model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    

@router.get('/tasks/{task_id}')
async def task_status(task_id: str):
    try:
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=400, detail="Invalid Task ID format")
        task = await task_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=400, detail="No such Task exists")
        task_status = task.get("status", "Unknown. Please wait as we are looking into the issue...")
        return JSONResponse(status_code=200, content={'task_status': task_status})
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")