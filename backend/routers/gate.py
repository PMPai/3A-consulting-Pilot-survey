from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas

router = APIRouter(prefix="/api", tags=["gate"])

# Thresholds (configurable)
BENEFIT_MIN = 500000.0       # annual potential benefit >= 500k
DIFFICULTY_MAX = 3.5         # avg difficulty <= 3.5
RULE_MIN = 3                 # R4 rule clarity >= 3
DATA_MIN = 3                 # avg(R1,R2,R3) >= 3
LEADERSHIP_MIN = 4           # R7 >= 4
COMPLIANCE_MAX = 3           # R8 risk <= 3


@router.post("/gate", response_model=schemas.GateOut)
def upsert_gate(payload: schemas.GateCreate, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=payload.survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")

    procs = db.query(models.Process).filter_by(survey_id=s.id).all()
    best_benefit = max((p.roi.annual_potential_benefit for p in procs if p.roi), default=0)

    ar = s.ai_readiness
    diff = None
    if ar:
        vals = [ar.r1_data_digital, ar.r2_data_structured, ar.r3_data_quality,
                ar.r4_rule_clarity, ar.r5_it_infra, ar.r6_user_acceptance,
                ar.r7_leadership_support]
        vals = [v or 0 for v in vals]
        avg7 = sum(vals) / 7.0
        r8 = ar.r8_compliance_risk or 3
        diff = (avg7 * 7 + (6 - r8)) / 8.0

    data_avg = None
    if ar and ar.r1_data_digital and ar.r2_data_structured and ar.r3_data_quality:
        data_avg = (ar.r1_data_digital + ar.r2_data_structured + ar.r3_data_quality) / 3.0

    budget_match = True
    if s.expectations and s.expectations.budget_range:
        # simple match: any budget choice acceptable for pilot
        budget_match = not s.expectations.budget_range.startswith("<30") or best_benefit >= 200000

    checks = {
        "benefit_threshold": best_benefit >= BENEFIT_MIN,
        "difficulty_pass": (diff is not None and diff <= DIFFICULTY_MAX),
        "rule_pass": (ar is not None and (ar.r4_rule_clarity or 0) >= RULE_MIN),
        "data_pass": (data_avg is not None and data_avg >= DATA_MIN),
        "leadership_pass": (ar is not None and (ar.r7_leadership_support or 0) >= LEADERSHIP_MIN),
        "compliance_pass": (ar is not None and (ar.r8_compliance_risk or 5) <= COMPLIANCE_MAX),
        "budget_match": budget_match,
    }

    all_pass = all(checks.values())
    conclusion = payload.conclusion or ("suitable" if all_pass else "not_suitable")

    # recommended pilot: highest-benefit process that is also "easy enough"
    recommended = payload.recommended_pilot_process_id
    if not recommended:
        candidates = sorted(
            [p for p in procs if p.roi],
            key=lambda x: (x.roi.annual_potential_benefit or 0), reverse=True,
        )
        if candidates:
            recommended = candidates[0].id

    if s.gate_check:
        for k, v in checks.items():
            setattr(s.gate_check, k, v)
        s.gate_check.conclusion = conclusion
        s.gate_check.recommended_pilot_process_id = recommended
        s.gate_check.recommendation_reason = payload.recommendation_reason
        db.commit()
        db.refresh(s.gate_check)
        return s.gate_check

    g = models.Stage2GateCheck(
        survey_id=s.id,
        conclusion=conclusion,
        recommended_pilot_process_id=recommended,
        recommendation_reason=payload.recommendation_reason,
        **checks,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g
