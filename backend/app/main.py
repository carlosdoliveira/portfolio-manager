
from fastapi import FastAPI, UploadFile, File
from app.services.importer import import_b3_excel
from app.db.database import init_db

app = FastAPI(title="B3 Portfolio MVP")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/import/b3")
async def import_b3(file: UploadFile = File(...)):
    result = import_b3_excel(file)
    return {"status": "ok", "imported": result}
