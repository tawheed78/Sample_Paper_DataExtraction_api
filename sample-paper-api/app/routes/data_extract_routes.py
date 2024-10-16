import json
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from ..models import PaperModel
from ..config import db, instruction, prompt
from fastapi import APIRouter, HTTPException,File, UploadFile
import google.generativeai as genai
from dotenv import load_dotenv
from google.protobuf.json_format import MessageToDict
import os
import aiofiles
load_dotenv()

collection = db['sample_papers']

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction=instruction,
    generation_config={"response_mime_type": "application/json"}
)

router = APIRouter()

@router.post('/extract/pdf')
async def extract_pdf(file: UploadFile = File(...)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        file_location = f"data/input/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, 'wb') as out_file:
            content = await file.read()  # Read the file content
            out_file.write(content)
        sample_pdf = genai.upload_file(file_location)
        response = model.generate_content([prompt, sample_pdf])
        # try:
        #     response = json.loads(response.text)  # Parse the response to a dict
        # except json.JSONDecodeError as e:
        #     raise HTTPException(status_code=400, detail=f"Invalid JSON response: {str(e)}")
        response = json.loads(response.text)
        # print(response)
        try:
            sample_paper = PaperModel(**response)
            print(sample_paper)
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
        result = collection.insert_one(sample_paper.model_dump())
        #return JSONResponse(status_code=201, content={'Paper added successfully'})
       
    except Exception as e:
        print(e)