"""
Sample paper routes for ZuAI Sample Paper FastAPI application.

This module defines the API endpoints for creating, retrieving,
updating, and deleting sample papers.
"""
import json
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from pydantic import ValidationError
import redis.asyncio as aioredis


from app.models import PaperModel,UpddatePaperModel, SearchResponseModel, SearchPaperResponseModel
from app.config import db, get_redis_client
from app.rate_limiter import rate_limit

router = APIRouter()
collection = db['sample_papers']

"Can Comment out this after running the server once."
# try:
#     index_name = collection.create_index(
#       [("sections.questions.question", "text"), ("sections.questions.answer", "text")]
#     )
#     print(f"Index created")
# except Exception as e:
#     print(f"Error creating index: {e}")


@router.post('/papers')
@rate_limit(limit=5, time_window=60)
async def create_sample_paper(
    request: Request,
    paper: PaperModel
    ):
    "Create a new sample paper."
    try:
        paper_data = paper.model_dump()
        result = await collection.insert_one(paper_data)
        paper_id = result.inserted_id
        return JSONResponse(status_code=201, content={'paper_id': str(paper_id)})
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {ve}") from ve
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e

@router.get('/papers/{paper_id}')
@rate_limit(limit=10, time_window=60)
async def get_sample_paper(
    request:Request,
    paper_id:str,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    "Retrieve a sample paper."
    try:
        cached_paper = await redis.get(paper_id)
        if cached_paper:
            cached_paper_data = json.loads(cached_paper)
            sample_paper = PaperModel(**cached_paper_data)
            return sample_paper
        query = {'_id': ObjectId(paper_id)}
        result = await collection.find_one(query)
        if result:
            result['_id'] = str(result['_id'])
            sample_paper = PaperModel(**result)
            await redis.set(paper_id, json.dumps(sample_paper.model_dump()), ex=3600)
            return sample_paper
        raise HTTPException(status_code=404, detail="Sample Paper not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e

@router.put('/papers/{paper_id}')
@rate_limit(limit=3, time_window=60)
async def update_sample_paper(
    request:Request,
    paper_id: str,
    update_paper_data: UpddatePaperModel,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    "Update an existing sample paper."
    try:
        query = {"_id": ObjectId(paper_id)}
        #update_data = {"$set": jsonable_encoder(update_paper_data)}
        update_data = {"$set": jsonable_encoder(update_paper_data.model_dump(exclude_unset=True))}
        result = await collection.update_one(query, update_data)

        if result.modified_count == 0:
            return JSONResponse(status_code=200, content={'message': "No changes made"})
        if result.modified_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            return JSONResponse(
                status_code=200,
                content={'message': "Sample paper updated successfully"}
                )
        raise HTTPException(
            status_code=404,
            detail="Sample Paper not found or not updated"
            )
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating Sample Paper: {e}") from e

@router.delete('/papers/{paper_id}')
@rate_limit(limit=5, time_window=60)
async def delete_sample_paper(
    request:Request,
    paper_id: str,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    "Delete a sample paper."
    try:
        query = {'_id': ObjectId(paper_id)}
        result = await collection.delete_one(query)
        if result.deleted_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            return JSONResponse(
                status_code=200,
                content={'message': f"Sample Paper with Paper ID: {paper_id} deleted successfully"}
                )
        raise HTTPException(status_code=404, detail=f"Paper with Paper ID: {paper_id} not found")
    except PyMongoError as pme:
        raise HTTPException(status_code=503, detail=f"Database error: {pme}") from pme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e

async def search(query_params: dict):
    "Searches for the required query params in database and returns the list of papers"
    try:
        result_cursor = collection.find(query_params)
        results = await result_cursor.to_list(length=10)
        return results
    except PyMongoError as e:
        raise HTTPException(status_code=503,
            detail="Database error while searching for paper") from e
    except Exception as e:
        raise HTTPException(status_code=500,
            detail="Internal server error during search") from e

@router.get('/papers/search/')
@rate_limit(limit=20, time_window=60)
async def search_papers(
    request: Request,
    query: str = Query(..., description="Query string to search papers")
    ):
    """Search for sample paper by quering on questions and answer fields.
    Returns li"""
    try:
        query_params = {"$text": {"$search": query }}
        result = await search(query_params)
        if not result:
            raise HTTPException(status_code=404,
                detail="No sample papers found for the given query")
        sample_papers = []
        for res in result:
            try:
                paper_id = str(res["_id"])
                paper_title = res.get("title", "Untitled")
                paper_subject = res.get("params", {}).get("subject", "Unknown Subject")
                sample_papers.append(SearchPaperResponseModel(paper_id=paper_id,
                    title=paper_title, subject=paper_subject))
            except Exception as e:
                raise HTTPException(status_code=500,
                    detail="Internal server error during search") from e
        return SearchResponseModel(
            message=f"{len(sample_papers)} papers found for query: '{query}'",
            results=sample_papers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e
