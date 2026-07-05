from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, String, Boolean, DateTime, Float, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from database import Base


class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200))
    dept_name = Column(String(100))
    dept_size = Column(Integer)
    respondent_name = Column(String(100))
    respondent_title = Column(String(100))
    tenure_years = Column(Integer)
    responsibility = Column(Text)
    interview_date = Column(String(20))
    consultant_name = Column(String(100))
    status = Column(String(20), default="draft")  # draft / submitted
    created_at = Column(DateTime, default=datetime.utcnow)

    processes = relationship("Process", back_populates="survey", cascade="all, delete-orphan")
    opportunity_costs = relationship("OpportunityCost", back_populates="survey", uselist=False, cascade="all, delete-orphan")
    ai_readiness = relationship("AIReadiness", back_populates="survey", uselist=False, cascade="all, delete-orphan")
    expectations = relationship("Expectations", back_populates="survey", uselist=False, cascade="all, delete-orphan")
    gate_check = relationship("Stage2GateCheck", back_populates="survey", uselist=False, cascade="all, delete-orphan")


class Process(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    seq = Column(Integer)
    name = Column(String(200))
    purpose = Column(Text)
    frequency = Column(String(20))
    systems_used = Column(String(300))
    data_form = Column(String(50))
    pain_points = Column(Text)

    # score-based fields (1-5)
    hours_score = Column(Integer)        # monthly hours
    rate_score = Column(Integer)         # staff hourly rate level

    survey = relationship("Survey", back_populates="processes")
    details = relationship("ProcessDetail", back_populates="process", uselist=False, cascade="all, delete-orphan")
    steps = relationship("ProcessStep", back_populates="process", cascade="all, delete-orphan")
    uploads = relationship("ProcessUpload", back_populates="process", cascade="all, delete-orphan")
    error_costs = relationship("ErrorCost", back_populates="process", uselist=False, cascade="all, delete-orphan")
    roi = relationship("ROICalculation", back_populates="process", uselist=False, cascade="all, delete-orphan")


class ProcessDetail(Base):
    __tablename__ = "process_details"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    automation_current = Column(String(50))   # full_manual / partial_script / has_rpa
    exception_handling = Column(Text)
    supplementary_desc = Column(Text)

    process = relationship("Process", back_populates="details")


class ProcessStep(Base):
    __tablename__ = "process_steps"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    step_no = Column(Integer)
    step_name = Column(String(300))
    tool_used = Column(String(200))
    judgment_level = Column(String(20))  # rule / half / experience
    is_decision = Column(Boolean, default=False)   # 決策點 (fork)
    is_merge = Column(Boolean, default=False)       # 合流點 (join)
    branch_id = Column(Integer, ForeignKey("step_branches.id", ondelete="SET NULL"), nullable=True)

    process = relationship("Process", back_populates="steps")
    branches = relationship("StepBranch", back_populates="step",
                            cascade="all, delete-orphan",
                            foreign_keys="StepBranch.step_id")


class StepBranch(Base):
    __tablename__ = "step_branches"
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("process_steps.id", ondelete="CASCADE"))
    branch_no = Column(Integer)
    condition_desc = Column(String(300))                # 「評分 ≥ 700」
    merge_to_step_no = Column(Integer, nullable=True)    # 合流回主流程的步驟號
    next_action_text = Column(String(200), nullable=True)
    is_endpoint = Column(Boolean, default=False)         # True=流程結束（不合流）

    step = relationship("ProcessStep", back_populates="branches",
                        foreign_keys=[step_id])


class ProcessUpload(Base):
    __tablename__ = "process_uploads"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    upload_type = Column(String(20))   # sop / flowchart / other
    filename = Column(String(200))     # stored filename
    original_name = Column(String(300))
    mime = Column(String(100))
    size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    process = relationship("Process", back_populates="uploads")


class ErrorCost(Base):
    __tablename__ = "error_costs"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    err_count_score = Column(Integer)   # 1-5
    err_cost_score = Column(Integer)    # 1-5
    error_types = Column(String(200))   # comma-separated
    complaint_level = Column(String(20))  # none / occasional / frequent

    process = relationship("Process", back_populates="error_costs")


class OpportunityCost(Base):
    __tablename__ = "opportunity_costs"
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    delayed_process_id = Column(Integer, ForeignKey("processes.id", ondelete="SET NULL"), nullable=True)
    avg_delay_days = Column(String(20))
    delay_loss_score = Column(Integer)       # 1-5
    lost_opp_score = Column(Integer)         # 1-5
    extra_rev_score = Column(Integer)        # 1-5

    survey = relationship("Survey", back_populates="opportunity_costs")
    delayed_process = relationship("Process")


class AIReadiness(Base):
    __tablename__ = "ai_readiness_scores"
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    r1_data_digital = Column(Integer)
    r2_data_structured = Column(Integer)
    r3_data_quality = Column(Integer)
    r4_rule_clarity = Column(Integer)
    r5_it_infra = Column(Integer)
    r6_user_acceptance = Column(Integer)
    r7_leadership_support = Column(Integer)
    r8_compliance_risk = Column(Integer)

    survey = relationship("Survey", back_populates="ai_readiness")


class Expectations(Base):
    __tablename__ = "expectations"
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    expected_saving_score = Column(Integer)  # 1-5
    reallocated_to = Column(String(100))
    desired_timeline = Column(String(50))
    solution_types = Column(String(100))
    budget_range = Column(String(50))
    success_definition = Column(Text)
    main_concerns = Column(String(200))   # comma-separated

    survey = relationship("Survey", back_populates="expectations")


class ROICalculation(Base):
    __tablename__ = "roi_calculations"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    mode = Column(String(20), default="score")  # score / manual
    time_cost_yearly = Column(Float)
    error_cost_yearly = Column(Float)
    opportunity_cost_yearly = Column(Float)
    saving_pct = Column(Float)            # 0-100
    annual_potential_benefit = Column(Float)
    difficulty_score = Column(Float)      # avg of R1-R8 (excluding R8 reversed)
    rule_clarity_score = Column(Float)
    data_readiness_score = Column(Float)
    priority = Column(Integer)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    process = relationship("Process", back_populates="roi")


class Stage2GateCheck(Base):
    __tablename__ = "stage2_gate_checks"
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    benefit_threshold = Column(Boolean)
    difficulty_pass = Column(Boolean)
    rule_pass = Column(Boolean)
    data_pass = Column(Boolean)
    leadership_pass = Column(Boolean)
    compliance_pass = Column(Boolean)
    budget_match = Column(Boolean)
    conclusion = Column(String(20))   # suitable / not_suitable
    recommended_pilot_process_id = Column(Integer, ForeignKey("processes.id", ondelete="SET NULL"), nullable=True)
    recommendation_reason = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)

    survey = relationship("Survey", back_populates="gate_check")
