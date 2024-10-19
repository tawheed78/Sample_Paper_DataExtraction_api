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

from app.models import PaperModel,UpdatePaperModel, SearchResponseModel, SearchPaperResponseModel
#from app.config import db, get_redis_client
from app.configs.database import db
from app.configs.redis import get_redis_client
from app.configs.logs import logger
from app.rate_limiter import rate_limit

router = APIRouter()
collection = db['sample_papers']

"Can Comment out this after running the server once."
# try:
#     index_name = collection.create_index(
#       [("sections.questions.question", "text"), ("sections.questions.answer", "text")]
#     )
    # logger.debug("Index Created")
#     print(f"Index created")
# except Exception as e:
#     print(f"Error creating index: {e}")


@router.post('/papers')
@rate_limit(limit=5, time_window=60)
async def create_sample_paper(
    request: Request,
    paper: PaperModel
    ):
    """Create a new sample paper.
    This endpoint receives a request to create a sample paper and stores it in the database.

    Args:
        request (Request): The incoming request object.
        paper (PaperModel): The data model representing the sample paper to be created.

    Returns:
        JSONResponse: A response indicating the creation status and the ID of the newly created paper.
    """
    logger.info(f"POST /papers - Request received to create sample paper from {request.client.host}")
    try:
        paper_data = paper.model_dump()
        result = await collection.insert_one(paper_data)
        paper_id = result.inserted_id
        logger.info(f"Sample paper created successfully with ID: {paper_id}")
        return JSONResponse(status_code=201, content={'paper_id': str(paper_id)})
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail="Validation error")
    except PyMongoError as pme:
        logger.error(f"Database error while creating sample paper: {pme}")
        raise HTTPException(status_code=503, detail="Database error Occured")
    except Exception as e:
        logger.error(f"Internal Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server error")

@router.get('/papers/{paper_id}')
@rate_limit(limit=10, time_window=60)
async def get_sample_paper(
    request:Request,
    paper_id:str,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    """
    Retrieves a sample paper.

    This endpoint fetches a sample paper either from the cache or the database.

    Args:
        request (Request): The incoming request object.
        paper_id (str): The ID of the sample paper to retrieve.
        redis : Redis client for caching.

    Returns:
        PaperModel: The requested sample paper if found.

    Raises:
        HTTPException: If the paper is not found or there is a database error.
    """
    logger.info(f"GET /papers/{paper_id} - Request received from {request.client.host}")
    try:
        cached_paper = await redis.get(paper_id)
        if cached_paper:
            logger.info(f"Paper {paper_id} retrieved from cache")
            cached_paper_data = json.loads(cached_paper)
            sample_paper = PaperModel(**cached_paper_data)
            return sample_paper
        logger.info(f"Paper {paper_id} not found in cache. Fetching from database.")
        query = {'_id': ObjectId(paper_id)}
        result = await collection.find_one(query)
        if result:
            result['_id'] = str(result['_id'])
            sample_paper = PaperModel(**result)
            await redis.set(paper_id, json.dumps(sample_paper.model_dump()), ex=3600)
            logger.info(f"Paper {paper_id} retrieved from database and cached")
            return sample_paper
        logger.warning(f"Paper: {paper_id} not found in database")
        raise HTTPException(status_code=404, detail="Sample Paper not found")
    except PyMongoError as pme:
        logger.error(f"Database error while fetching paper - {paper_id}: {pme}")
        raise HTTPException(status_code=503, detail=f"Database error occured.") from pme
    except Exception as e:
        logger.error(f"Internal Server error while fetching paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server error") from e

@router.put('/papers/{paper_id}')
@rate_limit(limit=3, time_window=60)
async def update_sample_paper(
    request:Request,
    paper_id: str,
    update_paper_data: UpdatePaperModel,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    """
    Update an existing sample paper.

    This endpoint updates the details of a sample paper in the database. Partial updates allowed.

    Args:
        request (Request): The incoming request object.
        paper_id (str): The ID of the sample paper to update.
        update_paper_data (UpddatePaperModel): The updated data for the sample paper.
        redis : Redis client for caching.

    Returns:
        JSONResponse: A response indicating the update status.

    Raises:
        HTTPException: If the paper is not found or there is a database error.
    """
    logger.info(f"PUT /papers/{paper_id} - Request received to update paper from {request.client.host}")
    try:
        query = {"_id": ObjectId(paper_id)}
        #update_data = {"$set": jsonable_encoder(update_paper_data)}
        update_data = {"$set": jsonable_encoder(update_paper_data.model_dump(exclude_unset=True))}
        result = await collection.update_one(query, update_data)

        if result.modified_count == 0:
            logger.info(f"No changes made to paper {paper_id}")
            return JSONResponse(status_code=200, content={'message': "No changes made"})
        if result.modified_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            logger.info(f"Sample paper {paper_id} updated successfully")
            return JSONResponse(
                status_code=200,
                content={'message': "Sample paper updated successfully"}
                )
        logger.warning(f"Paper {paper_id} not found or not updated")
        raise HTTPException(
            status_code=404,
            detail="Sample Paper not found or not updated"
            )
    except PyMongoError as pme:
        logger.error(f"Database error while updating paper {paper_id}: {pme}")
        raise HTTPException(status_code=503, detail="Database error occured.") from pme
    except Exception as e:
        logger.error(f"Error updating Sample Paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating Sample Paper.") from e

@router.delete('/papers/{paper_id}')
@rate_limit(limit=5, time_window=60)
async def delete_sample_paper(
    request:Request,
    paper_id: str,
    redis: aioredis.Redis = Depends(get_redis_client)
    ):
    """
    Delete a sample paper.

    This endpoint deletes a sample paper from the database.

    Args:
        request (Request): The incoming request object.
        paper_id (str): The ID of the sample paper to delete.
        redis : Redis client for caching.

    Returns:
        JSONResponse: A response showing the deletion status.

    Raises:
        HTTPException: If the paper is not found or there is a database error.
    """
    logger.info(f"DELETE /papers/{paper_id} - Request received from {request.client.host}")
    try:
        query = {'_id': ObjectId(paper_id)}
        result = await collection.delete_one(query)
        if result.deleted_count == 1:
            cached_paper = await redis.get(paper_id)
            if cached_paper:
                await redis.delete(paper_id)
            logger.info(f"Sample paper {paper_id} deleted successfully")
            return JSONResponse(
                status_code=200,
                content={'message': f"Sample Paper with Paper ID: {paper_id} deleted successfully"}
                )
        logger.warning(f"Paper with Paper ID: {paper_id} not found")
        raise HTTPException(status_code=404, detail=f"Paper with Paper ID: {paper_id} not found")
    except PyMongoError as pme:
        logger.error(f"Database error while deleting paper {paper_id}: {pme}")
        raise HTTPException(status_code=503, detail="Database error occured.") from pme
    except Exception as e:
        logger.error(f"Internal Server error while deleting paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server error") from e

async def search(query_params: dict):
    """
    Search for sample papers in the database.

    This function queries the database using the provided parameters.

    Args:
        query_params (dict): The query parameters for searching sample papers.

    Returns:
        list: A list of sample papers matching the query.

    Raises:
        HTTPException: If there is a database error.
    """
    try:
        score = {"score": {"$meta": "textScore"}}
        result_cursor = collection.find(query_params, score).sort([("score", {"$meta": "textScore"})])
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
    """
    Search for sample papers by querying on questions and answer fields.

    This endpoint returns a list of paper_id, paper_title, paper_subject of all the papers that match the search criteria.

    Args:
        request (Request): The incoming request object.
        query (str): The query string used to search for sample papers.

    Returns:
        SearchResponseModel: A model containing the search results.

    Raises:
        HTTPException: If no papers are found or there is an internal error during search.
    """
    logger.info(f"GET /papers/search/ - Search query '{query}' received from {request.client.host}")
    try:
        query_params = {"$text": {"$search": query }}
        result = await search(query_params)
        if not result:
            logger.warning(f"No sample papers found for query '{query}'")
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
        logger.info(f"Found {len(sample_papers)} papers for query '{query}'")
        return SearchResponseModel(
            message=f"{len(sample_papers)} papers found for query: '{query}'",
            results=sample_papers
        )
    except Exception as e:
        logger.error(f"Internal Server error during search for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server error: {e}") from e
