from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import database

app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator Backend powered by FastAPI, SQLite Database, and Google Gemini 1.5 Pro",
    version="1.1.0"
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_db_event():
    database.init_db()

# Enable CORS for local Streamlit & Web Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include application routes
app.include_router(router)

@app.get("/", tags=["Health & Info"])
async def root():
    """
    Root endpoint for health checks and API status.
    """
    return {
        "app": "LegalEase Backend API",
        "status": "online",
        "database": "SQLite (legalease.db) Active",
        "model": "Gemini 1.5 Pro Integration",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
