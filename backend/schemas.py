from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, conint


def _dt(v):
    if isinstance(v, datetime):
        return v.isoformat()
    return v


# ---------- Survey ----------
class SurveyBase(BaseModel):
    company: Optional[str] = None
    dept_name: Optional[str] = None
    dept_size: Optional[int] = None
    respondent_name: Optional[str] = None
    respondent_title: Optional[str] = None
    tenure_years: Optional[int] = None
    responsibility: Optional[str] = None
    interview_date: Optional[str] = None
    consultant_name: Optional[str] = None
    status: Optional[str] = "draft"


class SurveyCreate(SurveyBase):
    pass


class SurveyOut(SurveyBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ---------- Process ----------
class ProcessBase(BaseModel):
    seq: Optional[int] = 1
    name: Optional[str] = None
    purpose: Optional[str] = None
    frequency: Optional[str] = None
    systems_used: Optional[str] = None
    data_form: Optional[str] = None
    pain_points: Optional[str] = None
    hours_score: Optional[int] = Field(None, ge=1, le=5)
    rate_score: Optional[int] = Field(None, ge=1, le=5)


class ProcessCreate(ProcessBase):
    pass


class ProcessOut(ProcessBase):
    id: int
    survey_id: int

    class Config:
        from_attributes = True


# ---------- Process Detail ----------
class ProcessDetailBase(BaseModel):
    automation_current: Optional[str] = None
    exception_handling: Optional[str] = None
    supplementary_desc: Optional[str] = None


class ProcessDetailCreate(ProcessDetailBase):
    pass


class ProcessDetailOut(ProcessDetailBase):
    id: int
    process_id: int

    class Config:
        from_attributes = True


# ---------- Step ----------
class StepBase(BaseModel):
    step_no: Optional[int] = 1
    step_name: Optional[str] = None
    tool_used: Optional[str] = None
    judgment_level: Optional[str] = None
    is_decision: Optional[bool] = False
    is_merge: Optional[bool] = False
    branch_id: Optional[int] = None


class StepCreate(StepBase):
    pass


class StepOut(StepBase):
    id: int
    process_id: int

    class Config:
        from_attributes = True


# ---------- Step Branch ----------
class StepBranchBase(BaseModel):
    branch_no: Optional[int] = 1
    condition_desc: Optional[str] = None
    merge_to_step_no: Optional[int] = None
    next_action_text: Optional[str] = None
    is_endpoint: Optional[bool] = False


class StepBranchCreate(StepBranchBase):
    pass


class StepBranchOut(StepBranchBase):
    id: int
    step_id: int

    class Config:
        from_attributes = True


# ---------- Upload ----------
class UploadOut(BaseModel):
    id: int
    process_id: int
    upload_type: str
    filename: str
    original_name: str
    mime: Optional[str] = None
    size: int
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Error Cost ----------
class ErrorCostBase(BaseModel):
    err_count_score: Optional[int] = Field(None, ge=1, le=5)
    err_cost_score: Optional[int] = Field(None, ge=1, le=5)
    error_types: Optional[str] = None
    complaint_level: Optional[str] = None


class ErrorCostCreate(ErrorCostBase):
    pass


class ErrorCostOut(ErrorCostBase):
    id: int
    process_id: int

    class Config:
        from_attributes = True


# ---------- Opportunity Cost ----------
class OpportunityCostBase(BaseModel):
    delayed_process_id: Optional[int] = None
    avg_delay_days: Optional[str] = None
    delay_loss_score: Optional[int] = Field(None, ge=1, le=5)
    lost_opp_score: Optional[int] = Field(None, ge=1, le=5)
    extra_rev_score: Optional[int] = Field(None, ge=1, le=5)


class OpportunityCostCreate(OpportunityCostBase):
    pass


class OpportunityCostOut(OpportunityCostBase):
    id: int
    survey_id: int

    class Config:
        from_attributes = True


# ---------- AI Readiness ----------
class AIReadinessBase(BaseModel):
    r1_data_digital: Optional[int] = Field(None, ge=1, le=5)
    r2_data_structured: Optional[int] = Field(None, ge=1, le=5)
    r3_data_quality: Optional[int] = Field(None, ge=1, le=5)
    r4_rule_clarity: Optional[int] = Field(None, ge=1, le=5)
    r5_it_infra: Optional[int] = Field(None, ge=1, le=5)
    r6_user_acceptance: Optional[int] = Field(None, ge=1, le=5)
    r7_leadership_support: Optional[int] = Field(None, ge=1, le=5)
    r8_compliance_risk: Optional[int] = Field(None, ge=1, le=5)


class AIReadinessCreate(AIReadinessBase):
    pass


class AIReadinessOut(AIReadinessBase):
    id: int
    survey_id: int

    class Config:
        from_attributes = True


# ---------- Expectations ----------
class ExpectationsBase(BaseModel):
    expected_saving_score: Optional[int] = Field(None, ge=1, le=5)
    reallocated_to: Optional[str] = None
    desired_timeline: Optional[str] = None
    solution_types: Optional[str] = None
    budget_range: Optional[str] = None
    success_definition: Optional[str] = None
    main_concerns: Optional[str] = None


class ExpectationsCreate(ExpectationsBase):
    pass


class ExpectationsOut(ExpectationsBase):
    id: int
    survey_id: int

    class Config:
        from_attributes = True


# ---------- ROI ----------
class ROICreate(BaseModel):
    process_id: int
    mode: Optional[str] = "score"
    saving_pct: Optional[float] = None
    time_cost_yearly: Optional[float] = None
    error_cost_yearly: Optional[float] = None
    opportunity_cost_yearly: Optional[float] = None


class ROIOut(BaseModel):
    id: int
    process_id: int
    mode: str
    time_cost_yearly: Optional[float] = None
    error_cost_yearly: Optional[float] = None
    opportunity_cost_yearly: Optional[float] = None
    saving_pct: Optional[float] = None
    annual_potential_benefit: Optional[float] = None
    difficulty_score: Optional[float] = None
    rule_clarity_score: Optional[float] = None
    data_readiness_score: Optional[float] = None
    priority: Optional[int] = None
    calculated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Gate ----------
class GateCreate(BaseModel):
    survey_id: int
    conclusion: Optional[str] = None
    recommended_pilot_process_id: Optional[int] = None
    recommendation_reason: Optional[str] = None


class GateOut(BaseModel):
    id: int
    survey_id: int
    benefit_threshold: Optional[bool] = None
    difficulty_pass: Optional[bool] = None
    rule_pass: Optional[bool] = None
    data_pass: Optional[bool] = None
    leadership_pass: Optional[bool] = None
    compliance_pass: Optional[bool] = None
    budget_match: Optional[bool] = None
    conclusion: Optional[str] = None
    recommended_pilot_process_id: Optional[int] = None
    recommendation_reason: Optional[str] = None
    checked_at: Optional[datetime] = None

    class Config:
        from_attributes = True
