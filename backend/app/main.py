from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.services.importer import import_b3_excel
from app.db.database import init_db

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
