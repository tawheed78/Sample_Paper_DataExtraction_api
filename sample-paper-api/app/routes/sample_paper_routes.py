from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from ..models import PaperModel
from ..config import db
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pymongo.errors import PyMongoError

router = APIRouter()
collection = db['sample_papers']

@router.post('/papers')
async def create_sample_paper(paper: PaperModel):
    try:
        paper_data = paper.model_dump()
        result = await collection.insert_one(paper_data)
        paper_id = result.inserted_id
        return JSONResponse(status_code=201, content={'paper_id': str(paper_id)})
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {ve}")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")
    
@router.get('/papers/{paper_id}')
async def get_sample_paper(paper_id:str):
    try:
        result = await collection.find_one({'_id': ObjectId(paper_id)})
        if result:
            sample_paper = PaperModel(**result)
            return sample_paper
        else:
            raise HTTPException(status_code=404, detail="Sample Paper not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")
    
@router.put('/papers/{paper_id}')
async def update_sample_paper(paper_id: str, update_paper_data: PaperModel):
    try:
        result = await collection.update_one({"_id":ObjectId(paper_id)},{"$set": jsonable_encoder(update_paper_data)})
        if result.modified_count == 0:
            return JSONResponse(status_code=200, content={'message': "No changes made"})
        if result.modified_count == 1:
            return JSONResponse(status_code=200, content={'message': "Product updated successfully"})
        else:
            raise HTTPException(status_code=404, detail="Product not found or not updated")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error updating Product")

@router.delete('/papers/{paper_id}')
async def delete_sample_paper(paper_id: str):
    try:
        result = await collection.delete_one({'_id': ObjectId(paper_id)})
        if result.deleted_count == 1:
            return JSONResponse(status_code=200, content={'message': f"Sample Paper with Paper ID: {paper_id} deleted successfully"})
        else:
            raise HTTPException(status_code=404, detail=f"Sample Paper with Paper ID: {paper_id} not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")