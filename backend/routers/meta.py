from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas

router = APIRouter(prefix="/api/surveys", tags=["meta"])


# ---------- Opportunity Cost ----------
@router.post("/{survey_id}/opportunity_costs", response_model=schemas.OpportunityCostOut)
def upsert_opp(survey_id: int, payload: schemas.OpportunityCostCreate, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    if s.opportunity_costs:
        for k, v in payload.dict().items():
            setattr(s.opportunity_costs, k, v)
        db.commit()
        db.refresh(s.opportunity_costs)
        return s.opportunity_costs
    o = models.OpportunityCost(survey_id=survey_id, **payload.dict())
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


# ---------- AI Readiness ----------
@router.post("/{survey_id}/ai_readiness", response_model=schemas.AIReadinessOut)
def upsert_readiness(survey_id: int, payload: schemas.AIReadinessCreate, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    if s.ai_readiness:
        for k, v in payload.dict().items():
            setattr(s.ai_readiness, k, v)
        db.commit()
        db.refresh(s.ai_readiness)
        return s.ai_readiness
    a = models.AIReadiness(survey_id=survey_id, **payload.dict())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ---------- Expectations ----------
@router.post("/{survey_id}/expectations", response_model=schemas.ExpectationsOut)
def upsert_expectations(survey_id: int, payload: schemas.ExpectationsCreate, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    if s.expectations:
        for k, v in payload.dict().items():
            setattr(s.expectations, k, v)
        db.commit()
        db.refresh(s.expectations)
        return s.expectations
    e = models.Expectations(survey_id=survey_id, **payload.dict())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
