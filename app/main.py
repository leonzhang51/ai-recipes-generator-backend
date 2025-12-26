from fastapi import FastAPI
from app.api.routes import router as api_router
import uvicorn

app = FastAPI()

# Include API routes under /api
app.include_router(api_router, prefix="/api")

# Add CORS middleware to allow frontend dev origins
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)