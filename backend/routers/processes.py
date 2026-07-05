import os, uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import database, models, schemas
from database import UPLOAD_DIR

router = APIRouter(prefix="/api", tags=["processes"])


@router.post("/surveys/{survey_id}/processes", response_model=schemas.ProcessOut)
def create_process(survey_id: int, payload: schemas.ProcessCreate, db: Session = Depends(database.get_db)):
    if not db.query(models.Survey).filter_by(id=survey_id).first():
        raise HTTPException(404, "Survey not found")
    p = models.Process(survey_id=survey_id, **payload.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/processes/{process_id}", response_model=schemas.ProcessOut)
def get_process(process_id: int, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    return p


@router.put("/processes/{process_id}", response_model=schemas.ProcessOut)
def update_process(process_id: int, payload: schemas.ProcessCreate, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    for k, v in payload.dict().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/processes/{process_id}")
def delete_process(process_id: int, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


# ---------- Process Detail ----------
@router.post("/processes/{process_id}/detail", response_model=schemas.ProcessDetailOut)
def upsert_detail(process_id: int, payload: schemas.ProcessDetailCreate, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    if p.details:
        for k, v in payload.dict().items():
            setattr(p.details, k, v)
        db.commit()
        db.refresh(p.details)
        return p.details
    d = models.ProcessDetail(process_id=process_id, **payload.dict())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ---------- Steps ----------
@router.post("/processes/{process_id}/steps", response_model=schemas.StepOut)
def add_step(process_id: int, payload: schemas.StepCreate, db: Session = Depends(database.get_db)):
    if not db.query(models.Process).filter_by(id=process_id).first():
        raise HTTPException(404, "Process not found")
    st = models.ProcessStep(process_id=process_id, **payload.dict())
    db.add(st)
    db.commit()
    db.refresh(st)
    return st


@router.get("/processes/{process_id}/steps", response_model=List[schemas.StepOut])
def list_steps(process_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.ProcessStep).filter_by(process_id=process_id).order_by(models.ProcessStep.step_no).all()


@router.put("/steps/{step_id}", response_model=schemas.StepOut)
def update_step(step_id: int, payload: schemas.StepCreate, db: Session = Depends(database.get_db)):
    st = db.query(models.ProcessStep).filter_by(id=step_id).first()
    if not st:
        raise HTTPException(404, "Step not found")
    for k, v in payload.dict().items():
        setattr(st, k, v)
    db.commit()
    db.refresh(st)
    return st


@router.delete("/steps/{step_id}")
def delete_step(step_id: int, db: Session = Depends(database.get_db)):
    st = db.query(models.ProcessStep).filter_by(id=step_id).first()
    if not st:
        raise HTTPException(404, "Step not found")
    db.delete(st)
    db.commit()
    return {"ok": True}


# ---------- Step Branches ----------
@router.post("/steps/{step_id}/branches", response_model=schemas.StepBranchOut)
def add_branch(step_id: int, payload: schemas.StepBranchCreate, db: Session = Depends(database.get_db)):
    st = db.query(models.ProcessStep).filter_by(id=step_id).first()
    if not st:
        raise HTTPException(404, "Step not found")
    b = models.StepBranch(step_id=step_id, **payload.dict())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.get("/steps/{step_id}/branches", response_model=List[schemas.StepBranchOut])
def list_branches(step_id: int, db: Session = Depends(database.get_db)):
    return (db.query(models.StepBranch)
            .filter_by(step_id=step_id)
            .order_by(models.StepBranch.branch_no)
            .all())


@router.delete("/branches/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(database.get_db)):
    b = db.query(models.StepBranch).filter_by(id=branch_id).first()
    if not b:
        raise HTTPException(404, "Branch not found")
    # clear branch_id on child steps first
    db.query(models.ProcessStep).filter_by(branch_id=branch_id).update({"branch_id": None})
    db.delete(b)
    db.commit()
    return {"ok": True}


# ---------- Uploads ----------
MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".svg", ".gif"}


@router.post("/processes/{process_id}/uploads", response_model=schemas.UploadOut)
async def upload_file(
    process_id: int,
    upload_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    if not db.query(models.Process).filter_by(id=process_id).first():
        raise HTTPException(404, "Process not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"File type {ext} not allowed")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(413, "File too large (max 10MB)")

    stored = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, stored)
    with open(path, "wb") as f:
        f.write(data)

    u = models.ProcessUpload(
        process_id=process_id,
        upload_type=upload_type,
        filename=stored,
        original_name=file.filename,
        mime=file.content_type,
        size=len(data),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.get("/processes/{process_id}/uploads", response_model=List[schemas.UploadOut])
def list_uploads(process_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.ProcessUpload).filter_by(process_id=process_id).all()


@router.get("/uploads/{upload_id}/download")
def download_upload(upload_id: int, db: Session = Depends(database.get_db)):
    from fastapi.responses import FileResponse
    u = db.query(models.ProcessUpload).filter_by(id=upload_id).first()
    if not u:
        raise HTTPException(404, "Upload not found")
    path = os.path.join(UPLOAD_DIR, u.filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File missing on disk")
    return FileResponse(path, filename=u.original_name, media_type=u.mime or "application/octet-stream")


@router.delete("/uploads/{upload_id}")
def delete_upload(upload_id: int, db: Session = Depends(database.get_db)):
    u = db.query(models.ProcessUpload).filter_by(id=upload_id).first()
    if not u:
        raise HTTPException(404, "Upload not found")
    path = os.path.join(UPLOAD_DIR, u.filename)
    if os.path.exists(path):
        os.remove(path)
    db.delete(u)
    db.commit()
    return {"ok": True}


# ---------- Error Costs ----------
@router.post("/processes/{process_id}/error_costs", response_model=schemas.ErrorCostOut)
def upsert_error(process_id: int, payload: schemas.ErrorCostCreate, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    if p.error_costs:
        for k, v in payload.dict().items():
            setattr(p.error_costs, k, v)
        db.commit()
        db.refresh(p.error_costs)
        return p.error_costs
    e = models.ErrorCost(process_id=process_id, **payload.dict())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
