from fastapi import FastAPI
from backend.routes import upload, ask, extract

app = FastAPI(title="Ultra Doc Intelligence API")

app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(ask.router, prefix="/api/v1", tags=["Ask"])
app.include_router(extract.router, prefix="/api/v1", tags=["Extract"])


@app.get("/")
def root():
    return {"message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=4135, reload=True)