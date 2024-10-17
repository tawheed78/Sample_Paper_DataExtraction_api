import json, os, aiofiles
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from ..models import PaperModel
from ..config import db, instruction, prompt
from ..utils import text_cleanup
from fastapi import APIRouter, Body, HTTPException,File, UploadFile
import google.generativeai as genai
from dotenv import load_dotenv
from pymongo.errors import PyMongoError

load_dotenv()

collection = db['sample_papers']

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction=instruction,
    generation_config={"response_mime_type": "application/json"}
)

router = APIRouter()

@router.post('/extract/text')
async def extract_text(input_data: str = Body(...)):
    try:
        if not isinstance(input_data, str):
            raise HTTPException(status_code=400, detail="Only plain text are allowed.")
        response = model.generate_content([prompt, input_data])
        response = response.text
        try:
            sample_paper = PaperModel(**json.loads(response))
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
        result = collection.insert_one(sample_paper.model_dump())
        return {"message": "Sample paper extracted and saved successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON response from model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
        

async def generate_sample_paper(sample_pdf):
    try:
        response = model.generate_content([prompt, sample_pdf])  # Assuming model is synchronous1
        response = response.text
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid response from content generation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during content generation: {e}")

async def insert_sample_paper(response: dict):
    try:
        sample_paper = PaperModel(**response)  # Validate using Pydantic
        await collection.insert_one(sample_paper.model_dump())  # Async MongoDB insertion
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


@router.post('/extract/pdf')
async def extract_pdf(file: UploadFile = File(...)):
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
            raise HTTPException(status_code=500, detail=f"Error while reading/writing file to disk: {e}")
        try:
            sample_pdf = genai.upload_file(file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Uploading PDF: {e}")
        try:
            response = await generate_sample_paper(sample_pdf)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
        try:
            await insert_sample_paper(response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")
        return {"message": "Sample paper extracted and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {e}")