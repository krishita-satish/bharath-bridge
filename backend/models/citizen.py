"""Citizen profile data models matching DynamoDB schema from design doc."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CasteCategory(str, Enum):
    GENERAL = "general"
    OBC = "obc"
    SC = "sc"
    ST = "st"
    EWS = "ews"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class EducationLevel(str, Enum):
    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGHER_SECONDARY = "higher_secondary"
    GRADUATE = "graduate"
    POST_GRADUATE = "post_graduate"
    DOCTORATE = "doctorate"


class Occupation(str, Enum):
    FARMER = "farmer"
    DAILY_WAGE = "daily_wage"
    SELF_EMPLOYED = "self_employed"
    SALARIED = "salaried"
    STUDENT = "student"
    HOMEMAKER = "homemaker"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    OTHER = "other"


class Address(BaseModel):
    line1: str = ""
    line2: str = ""
    city: str = ""
    district: str = ""
    state: str = ""
    pincode: str = ""


class FamilyMember(BaseModel):
    name: str
    relationship: str  # e.g. "spouse", "child", "parent"
    age: int
    gender: Gender
    occupation: Optional[Occupation] = None
    income: Optional[float] = None


class CitizenProfile(BaseModel):
    """Full citizen profile — matches DynamoDB CitizenProfiles table schema."""

    citizen_id: str = Field(default="", description="Unique citizen identifier")
    name: str = ""
    date_of_birth: str = ""  # ISO 8601 format
    age: Optional[int] = None
    gender: Gender = Gender.MALE
    aadhaar_number: str = ""  # Will be encrypted in production
    pan_number: str = ""      # Will be encrypted in production
    phone: str = ""
    email: str = ""
    address: Address = Field(default_factory=Address)
    caste_category: CasteCategory = CasteCategory.GENERAL
    religion: str = ""
    annual_income: float = 0.0
    occupation: Occupation = Occupation.OTHER
    education: EducationLevel = EducationLevel.NONE
    is_bpl: bool = False  # Below Poverty Line
    is_disabled: bool = False
    disability_percentage: Optional[int] = None
    is_minority: bool = False
    is_pregnant: bool = False
    family_members: list[FamilyMember] = Field(default_factory=list)
    bank_account: str = ""  # Will be encrypted in production
    bank_ifsc: str = ""
    documents: list[str] = Field(default_factory=list)  # Document IDs
    digilocker_connected: bool = False
    consent_retention: bool = False
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

    @property
    def num_children(self) -> int:
        return sum(1 for m in self.family_members if m.relationship == "child")

    @property
    def num_daughters(self) -> int:
        return sum(
            1 for m in self.family_members
            if m.relationship == "child" and m.gender == Gender.FEMALE
        )

    @property
    def has_school_age_children(self) -> bool:
        return any(
            m.relationship == "child" and 6 <= m.age <= 18
            for m in self.family_members
        )
