from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
import database, models, schemas

router = APIRouter(prefix="/api/surveys", tags=["surveys"])


@router.post("", response_model=schemas.SurveyOut)
def create_survey(payload: schemas.SurveyCreate, db: Session = Depends(database.get_db)):
    s = models.Survey(**payload.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("", response_model=List[schemas.SurveyOut])
def list_surveys(db: Session = Depends(database.get_db)):
    return db.query(models.Survey).order_by(models.Survey.created_at.desc()).all()


@router.get("/{survey_id}", response_model=schemas.SurveyOut)
def get_survey(survey_id: int, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    return s


@router.put("/{survey_id}", response_model=schemas.SurveyOut)
def update_survey(survey_id: int, payload: schemas.SurveyCreate, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    for k, v in payload.dict().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{survey_id}")
def delete_survey(survey_id: int, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")
    db.delete(s)
    db.commit()
    return {"ok": True}


# Full nested fetch for consultant detail page
@router.get("/{survey_id}/full")
def get_survey_full(survey_id: int, db: Session = Depends(database.get_db)):
    s = db.query(models.Survey).filter_by(id=survey_id).first()
    if not s:
        raise HTTPException(404, "Survey not found")

    def proc_to_dict(p):
        return {
            "id": p.id, "seq": p.seq, "name": p.name, "purpose": p.purpose,
            "frequency": p.frequency, "systems_used": p.systems_used,
            "data_form": p.data_form, "pain_points": p.pain_points,
            "hours_score": p.hours_score, "rate_score": p.rate_score,
            "details": {
                "automation_current": p.details.automation_current if p.details else None,
                "exception_handling": p.details.exception_handling if p.details else None,
                "supplementary_desc": p.details.supplementary_desc if p.details else None,
            } if p.details else None,
            "steps": [
                {"id": st.id, "step_no": st.step_no, "step_name": st.step_name,
                 "tool_used": st.tool_used, "judgment_level": st.judgment_level,
                 "is_decision": st.is_decision, "is_merge": st.is_merge,
                 "branch_id": st.branch_id,
                 "branches": [
                     {"id": b.id, "branch_no": b.branch_no,
                      "condition_desc": b.condition_desc,
                      "merge_to_step_no": b.merge_to_step_no,
                      "next_action_text": b.next_action_text,
                      "is_endpoint": b.is_endpoint}
                     for b in st.branches
                 ]}
                for st in p.steps
            ],
            "uploads": [
                {"id": u.id, "upload_type": u.upload_type, "filename": u.filename,
                 "original_name": u.original_name, "mime": u.mime, "size": u.size,
                 "uploaded_at": u.uploaded_at.isoformat() if u.uploaded_at else None}
                for u in p.uploads
            ],
            "error_costs": {
                "err_count_score": p.error_costs.err_count_score if p.error_costs else None,
                "err_cost_score": p.error_costs.err_cost_score if p.error_costs else None,
                "error_types": p.error_costs.error_types if p.error_costs else None,
                "complaint_level": p.error_costs.complaint_level if p.error_costs else None,
            } if p.error_costs else None,
            "roi": {
                "id": p.roi.id, "mode": p.roi.mode,
                "time_cost_yearly": p.roi.time_cost_yearly,
                "error_cost_yearly": p.roi.error_cost_yearly,
                "opportunity_cost_yearly": p.roi.opportunity_cost_yearly,
                "saving_pct": p.roi.saving_pct,
                "annual_potential_benefit": p.roi.annual_potential_benefit,
                "difficulty_score": p.roi.difficulty_score,
                "rule_clarity_score": p.roi.rule_clarity_score,
                "data_readiness_score": p.roi.data_readiness_score,
                "priority": p.roi.priority,
            } if p.roi else None,
        }

    return {
        "survey": {
            "id": s.id, "company": s.company, "dept_name": s.dept_name,
            "dept_size": s.dept_size, "respondent_name": s.respondent_name,
            "respondent_title": s.respondent_title, "tenure_years": s.tenure_years,
            "responsibility": s.responsibility, "interview_date": s.interview_date,
            "consultant_name": s.consultant_name, "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        },
        "processes": [proc_to_dict(p) for p in s.processes],
        "opportunity_costs": {
            "id": s.opportunity_costs.id if s.opportunity_costs else None,
            "delayed_process_id": s.opportunity_costs.delayed_process_id if s.opportunity_costs else None,
            "avg_delay_days": s.opportunity_costs.avg_delay_days if s.opportunity_costs else None,
            "delay_loss_score": s.opportunity_costs.delay_loss_score if s.opportunity_costs else None,
            "lost_opp_score": s.opportunity_costs.lost_opp_score if s.opportunity_costs else None,
            "extra_rev_score": s.opportunity_costs.extra_rev_score if s.opportunity_costs else None,
        } if s.opportunity_costs else None,
        "ai_readiness": {
            "r1": s.ai_readiness.r1_data_digital if s.ai_readiness else None,
            "r2": s.ai_readiness.r2_data_structured if s.ai_readiness else None,
            "r3": s.ai_readiness.r3_data_quality if s.ai_readiness else None,
            "r4": s.ai_readiness.r4_rule_clarity if s.ai_readiness else None,
            "r5": s.ai_readiness.r5_it_infra if s.ai_readiness else None,
            "r6": s.ai_readiness.r6_user_acceptance if s.ai_readiness else None,
            "r7": s.ai_readiness.r7_leadership_support if s.ai_readiness else None,
            "r8": s.ai_readiness.r8_compliance_risk if s.ai_readiness else None,
        } if s.ai_readiness else None,
        "expectations": {
            "expected_saving_score": s.expectations.expected_saving_score if s.expectations else None,
            "reallocated_to": s.expectations.reallocated_to if s.expectations else None,
            "desired_timeline": s.expectations.desired_timeline if s.expectations else None,
            "solution_types": s.expectations.solution_types if s.expectations else None,
            "budget_range": s.expectations.budget_range if s.expectations else None,
            "success_definition": s.expectations.success_definition if s.expectations else None,
            "main_concerns": s.expectations.main_concerns if s.expectations else None,
        } if s.expectations else None,
        "gate_check": {
            "benefit_threshold": s.gate_check.benefit_threshold if s.gate_check else None,
            "difficulty_pass": s.gate_check.difficulty_pass if s.gate_check else None,
            "rule_pass": s.gate_check.rule_pass if s.gate_check else None,
            "data_pass": s.gate_check.data_pass if s.gate_check else None,
            "leadership_pass": s.gate_check.leadership_pass if s.gate_check else None,
            "compliance_pass": s.gate_check.compliance_pass if s.gate_check else None,
            "budget_match": s.gate_check.budget_match if s.gate_check else None,
            "conclusion": s.gate_check.conclusion if s.gate_check else None,
            "recommended_pilot_process_id": s.gate_check.recommended_pilot_process_id if s.gate_check else None,
            "recommendation_reason": s.gate_check.recommendation_reason if s.gate_check else None,
        } if s.gate_check else None,
    }
