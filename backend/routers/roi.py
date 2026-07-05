from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas

router = APIRouter(prefix="/api", tags=["roi"])


# Score -> reference value mappings
HOURS_MONTH = {1: 10, 2: 25, 3: 50, 4: 75, 5: 100}
RATE_HOUR = {1: 200, 2: 300, 3: 400, 4: 500, 5: 600}
ERR_COUNT = {1: 1, 2: 3, 3: 8, 4: 15, 5: 25}
ERR_COST = {1: 500, 2: 2000, 3: 5000, 4: 10000, 5: 20000}
DELAY_LOSS = {1: 1000, 2: 5000, 3: 15000, 4: 40000, 5: 100000}
LOST_OPP = {1: 0, 2: 5000, 3: 20000, 4: 50000, 5: 150000}
EXTRA_REV = {1: 0, 2: 10000, 3: 50000, 4: 150000, 5: 500000}
SAVING_PCT = {1: 10, 2: 30, 3: 50, 4: 70, 5: 90}


def compute_roi_for_process(p: models.Process, survey: models.Survey, saving_score: int = 3):
    """Compute ROI fields from score-based inputs."""
    time_y = (HOURS_MONTH.get(p.hours_score or 0, 0) * RATE_HOUR.get(p.rate_score or 0, 0)) * 12

    err_count = p.error_costs.err_count_score if p.error_costs else None
    err_cost = p.error_costs.err_cost_score if p.error_costs else None
    error_y = (ERR_COUNT.get(err_count or 0, 0) * ERR_COST.get(err_cost or 0, 0)) * 12

    opp = survey.opportunity_costs if survey.opportunity_costs else None
    opp_y = 0
    if opp:
        opp_y = (DELAY_LOSS.get(opp.delay_loss_score or 0, 0)
                 + LOST_OPP.get(opp.lost_opp_score or 0, 0)
                 + EXTRA_REV.get(opp.extra_rev_score or 0, 0)) * 12

    saving = SAVING_PCT.get(saving_score, 50)
    benefit = (time_y + error_y + opp_y) * saving / 100.0

    # readiness scores
    ar = survey.ai_readiness
    if ar:
        if ar.r1_data_digital and ar.r2_data_structured and ar.r3_data_quality:
            data_ready = (ar.r1_data_digital + ar.r2_data_structured + ar.r3_data_quality) / 3.0
        else:
            data_ready = 0
        rule = ar.r4_rule_clarity or 0
        # difficulty: avg of R1..R7 plus reversed R8 (higher risk = harder)
        vals = [ar.r1_data_digital, ar.r2_data_structured, ar.r3_data_quality,
                ar.r4_rule_clarity, ar.r5_it_infra, ar.r6_user_acceptance,
                ar.r7_leadership_support]
        vals = [v or 0 for v in vals]
        avg7 = sum(vals) / 7.0 if vals else 0
        r8 = ar.r8_compliance_risk or 3
        difficulty = (avg7 * 7 + (6 - r8)) / 8.0
    else:
        data_ready = 0
        rule = 0
        difficulty = 0

    return {
        "time_cost_yearly": time_y,
        "error_cost_yearly": error_y,
        "opportunity_cost_yearly": opp_y,
        "saving_pct": saving,
        "annual_potential_benefit": benefit,
        "difficulty_score": round(difficulty, 2),
        "rule_clarity_score": rule,
        "data_readiness_score": round(data_ready, 2),
    }


@router.post("/roi", response_model=schemas.ROIOut)
def create_or_update_roi(payload: schemas.ROICreate, db: Session = Depends(database.get_db)):
    p = db.query(models.Process).filter_by(id=payload.process_id).first()
    if not p:
        raise HTTPException(404, "Process not found")
    survey = p.survey

    saving_score = survey.expectations.expected_saving_score if survey.expectations and survey.expectations.expected_saving_score else 3
    calc = compute_roi_for_process(p, survey, saving_score)

    if payload.saving_pct is not None:
        calc["saving_pct"] = payload.saving_pct
        calc["annual_potential_benefit"] = (
            (calc["time_cost_yearly"] + calc["error_cost_yearly"] + calc["opportunity_cost_yearly"])
            * payload.saving_pct / 100.0
        )

    if payload.mode == "manual":
        for f in ("time_cost_yearly", "error_cost_yearly", "opportunity_cost_yearly"):
            v = getattr(payload, f)
            if v is not None:
                calc[f] = v
        calc["annual_potential_benefit"] = (
            (calc["time_cost_yearly"] + calc["error_cost_yearly"] + calc["opportunity_cost_yearly"])
            * calc["saving_pct"] / 100.0
        )

    if p.roi:
        for k, v in calc.items():
            setattr(p.roi, k, v)
        p.roi.mode = payload.mode
        db.commit()
        db.refresh(p.roi)
        roi = p.roi
    else:
        roi = models.ROICalculation(process_id=p.id, mode=payload.mode, **calc)
        db.add(roi)
        db.commit()
        db.refresh(roi)

    # recompute priorities for all processes of this survey
    procs = db.query(models.Process).filter_by(survey_id=survey.id).all()
    ranked = sorted(procs, key=lambda x: (x.roi.annual_potential_benefit if x.roi else 0), reverse=True)
    for i, pr in enumerate(ranked, 1):
        if pr.roi:
            pr.roi.priority = i
    db.commit()
    return roi


@router.get("/surveys/{survey_id}/rois", response_model=List[schemas.ROIOut])
def list_rois(survey_id: int, db: Session = Depends(database.get_db)):
    procs = db.query(models.Process).filter_by(survey_id=survey_id).all()
    out = []
    for p in procs:
        if p.roi:
            out.append(p.roi)
    return out
