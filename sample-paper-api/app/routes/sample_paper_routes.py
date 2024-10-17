import json
import redis.asyncio as aioredis
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from ..models import PaperModel, SearchResponseModel, SearchPaperResponseModel
from ..config import db, get_redis_client
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from pymongo.errors import PyMongoError
from pymongo import TEXT

router = APIRouter()
collection = db['sample_papers']

#collection.create_index([("sections.questions.question", TEXT)])




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
async def get_sample_paper(paper_id:str, redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        cached_paper = await redis.get(paper_id)
        if cached_paper:
            cached_paper_data = json.loads(cached_paper)
            sample_paper = PaperModel(**cached_paper_data)
            return sample_paper
        
        result = await collection.find_one({'_id': ObjectId(paper_id)})
        if result:
            result['_id'] = str(result['_id'])
            sample_paper = PaperModel(**result)
            await redis.set(paper_id, json.dumps(sample_paper), ex=3600)
            return sample_paper
        else:
            raise HTTPException(status_code=404, detail="Sample Paper not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")
    
@router.put('/papers/{paper_id}')
async def update_sample_paper(paper_id: str, update_paper_data: PaperModel, redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        result = await collection.update_one({"_id":ObjectId(paper_id)},{"$set": jsonable_encoder(update_paper_data)})
        if result.modified_count == 0:
            return JSONResponse(status_code=200, content={'message': "No changes made"})
        if result.modified_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            return JSONResponse(status_code=200, content={'message': "Sample paper updated successfully"})
        else:
            raise HTTPException(status_code=404, detail="Sample Paper not found or not updated")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating Sample Paper: {e}")

@router.delete('/papers/{paper_id}')
async def delete_sample_paper(paper_id: str, redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        result = await collection.delete_one({'_id': ObjectId(paper_id)})
        if result.deleted_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            return JSONResponse(status_code=200, content={'message': f"Sample Paper with Paper ID: {paper_id} deleted successfully"})
        else:
            raise HTTPException(status_code=404, detail=f"Sample Paper with Paper ID: {paper_id} not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")

async def search(query_params: dict):
    try:
        result_cursor = collection.find(query_params)
        results = await result_cursor.to_list(length=10)
        return results
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail="Database error while searching for papers")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error during search")


@router.get('/papers/search/')
async def search_papers(query: str = Query(..., description="Query string to search papers")):
    try:
        query_params = {"$text": {"$search": query }}
        result = await search(query_params)
        if not result:
            raise HTTPException(status_code=404, detail="No sample papers found for the given query")
        sample_papers = []
        for res in result:
            try:
                paper_id = str(res["_id"])
                paper_title = res.get("title", "Untitled")
                paper_subject = res.get("params", {}).get("subject", "Unknown Subject")
                sample_papers.append(SearchPaperResponseModel(paper_id=paper_id, title=paper_title, subject=paper_subject))
            except KeyError as e:
                # logger.error(f"Missing field in document {res['_id']}: {e}")
                continue
        return SearchResponseModel(
            message=f"{len(sample_papers)} papers found for query: '{query}'",
            results=sample_papers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}")