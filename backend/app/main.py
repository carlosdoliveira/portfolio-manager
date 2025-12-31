from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.importer import import_b3_excel
from app.db.database import init_db
from app.repositories.operations_repository import create_operation, list_operations


app = FastAPI(title="Portfolio Manager")

# 🔐 CORS CONFIG (DEV)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/import/b3")
async def import_b3(file: UploadFile = File(...)):
    summary = import_b3_excel(file)
    return {
        "status": "success",
        "summary": summary
    }

@app.post("/operations")
def create_manual_operation(payload: dict):
    try:
        payload["source"] = "MANUAL"
        create_operation(payload)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/operations")
def get_operations():
    return list_operations()