"""Scheme and eligibility rule data models matching Neptune graph schema."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SchemeCategory(str, Enum):
    MATERNITY = "maternity"
    SCHOLARSHIP = "scholarship"
    PENSION = "pension"
    HEALTHCARE = "healthcare"
    HOUSING = "housing"
    AGRICULTURE = "agriculture"
    EMPLOYMENT = "employment"
    INSURANCE = "insurance"
    GIRL_CHILD = "girl_child"
    ENERGY = "energy"
    ENTREPRENEURSHIP = "entrepreneurship"
    FOOD_SECURITY = "food_security"
    DISABILITY = "disability"
    EDUCATION = "education"
    FINANCIAL_INCLUSION = "financial_inclusion"


class RuleType(str, Enum):
    AGE_MIN = "age_min"
    AGE_MAX = "age_max"
    INCOME_MAX = "income_max"
    GENDER = "gender"
    CASTE = "caste"
    STATE = "state"
    OCCUPATION = "occupation"
    EDUCATION_MIN = "education_min"
    EDUCATION_MAX = "education_max"
    BPL = "bpl"
    DISABILITY = "disability"
    PREGNANT = "pregnant"
    HAS_CHILDREN = "has_children"
    HAS_DAUGHTERS = "has_daughters"
    MINORITY = "minority"
    CUSTOM = "custom"


class EligibilityRule(BaseModel):
    """A single eligibility condition — maps to Rule node in Neptune graph."""

    rule_id: str = ""
    rule_type: RuleType
    condition: str = ""  # e.g., "<=", ">=", "==", "in"
    value: str = ""      # e.g., "60", "female", "sc,st,obc"
    description: str = ""


class Scheme(BaseModel):
    """Government welfare scheme — maps to Scheme node in Neptune graph."""

    scheme_id: str
    name: str
    ministry: str
    category: SchemeCategory
    description: str = ""
    benefit_amount: float = 0.0  # in INR
    benefit_description: str = ""
    eligibility_rules: list[EligibilityRule] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    portal_url: str = ""
    deadline: Optional[str] = None  # ISO 8601
    application_process: str = ""
    state: Optional[str] = None  # None means all-India
    execution_tier: int = 2  # 1=API, 2=WebAutomation, 3=PDF
    approval_rate: float = 0.7  # Historical approval rate
    processing_days: int = 30  # Avg processing time
    # Graph relationships
    depends_on: list[str] = Field(default_factory=list)    # Scheme IDs
    conflicts_with: list[str] = Field(default_factory=list)  # Scheme IDs


class SchemeMatch(BaseModel):
    """Result of eligibility matching — a scheme matched to a citizen."""

    scheme: Scheme
    eligibility_score: float = 0.0  # 0.0 to 1.0
    matched_rules: list[str] = Field(default_factory=list)
    failed_rules: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    estimated_benefit: float = 0.0
    approval_probability: float = 0.0
    is_eligible: bool = False
    rank: int = 0
    conflicts: list[str] = Field(default_factory=list)
    unlocks: list[str] = Field(default_factory=list)  # Benefit chain schemes
