from fastapi import FastAPI
from .routes.sample_paper_routes import router as sample_paper_router
app = FastAPI()

app.include_router(sample_paper_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the ZuAI's Sample Paper API"}