from fastapi import FastAPI
from .routes.sample_paper_routes import router as sample_paper_router
from .routes.data_extract_routes import router as data_extract_router

app = FastAPI()

app.include_router(sample_paper_router)
app.include_router(data_extract_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the ZuAI's Sample Paper API"}