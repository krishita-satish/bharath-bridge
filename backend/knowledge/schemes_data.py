"""
15+ real Indian welfare schemes with structured eligibility rules,
required documents, benefit amounts, and inter-scheme relationships.
Covers Req 8: Knowledge Graph Management.
"""

from backend.models.scheme import (
    Scheme, EligibilityRule, RuleType, SchemeCategory,
)

SCHEMES: list[Scheme] = [
    # ── 1. PM-KISAN ──────────────────────────────────────────────────────
    Scheme(
        scheme_id="pm_kisan",
        name="PM-KISAN Samman Nidhi",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category=SchemeCategory.AGRICULTURE,
        description="Direct income support of ₹6,000/year to small and marginal farmers in three equal installments.",
        benefit_amount=6000,
        benefit_description="₹6,000 per year in 3 installments of ₹2,000",
        eligibility_rules=[
            EligibilityRule(rule_id="pmk_1", rule_type=RuleType.OCCUPATION, condition="==", value="farmer", description="Must be a farmer"),
            EligibilityRule(rule_id="pmk_2", rule_type=RuleType.INCOME_MAX, condition="<=", value="500000", description="Annual income ≤ ₹5 lakh"),
        ],
        required_documents=["aadhaar", "bank_statement", "income_certificate"],
        portal_url="https://pmkisan.gov.in",
        application_process="Online via PM-KISAN portal or through CSC centres",
        execution_tier=1,
        approval_rate=0.85,
        processing_days=21,
    ),

    # ── 2. PM Ujjwala Yojana ─────────────────────────────────────────────
    Scheme(
        scheme_id="pm_ujjwala",
        name="Pradhan Mantri Ujjwala Yojana",
        ministry="Ministry of Petroleum & Natural Gas",
        category=SchemeCategory.ENERGY,
        description="Free LPG connections to women from BPL households.",
        benefit_amount=1600,
        benefit_description="Free LPG connection + first refill and stove",
        eligibility_rules=[
            EligibilityRule(rule_id="uj_1", rule_type=RuleType.GENDER, condition="==", value="female", description="Applicant must be female"),
            EligibilityRule(rule_id="uj_2", rule_type=RuleType.BPL, condition="==", value="true", description="Must belong to BPL household"),
            EligibilityRule(rule_id="uj_3", rule_type=RuleType.AGE_MIN, condition=">=", value="18", description="Age ≥ 18"),
        ],
        required_documents=["aadhaar", "bpl_card", "bank_statement"],
        portal_url="https://www.pmujjwalayojana.com",
        execution_tier=2,
        approval_rate=0.80,
        processing_days=30,
    ),

    # ── 3. Pradhan Mantri Awas Yojana (PMAY) ────────────────────────────
    Scheme(
        scheme_id="pmay",
        name="Pradhan Mantri Awas Yojana (Gramin)",
        ministry="Ministry of Housing & Urban Affairs",
        category=SchemeCategory.HOUSING,
        description="Financial assistance for constructing pucca house for BPL families.",
        benefit_amount=120000,
        benefit_description="₹1,20,000 in plains / ₹1,30,000 in hilly areas",
        eligibility_rules=[
            EligibilityRule(rule_id="pmay_1", rule_type=RuleType.BPL, condition="==", value="true", description="BPL household"),
            EligibilityRule(rule_id="pmay_2", rule_type=RuleType.INCOME_MAX, condition="<=", value="300000", description="Annual income ≤ ₹3 lakh"),
        ],
        required_documents=["aadhaar", "income_certificate", "bpl_card", "bank_statement"],
        portal_url="https://pmaymis.gov.in",
        execution_tier=2,
        approval_rate=0.65,
        processing_days=90,
        depends_on=["pm_jan_dhan"],
    ),

    # ── 4. PM Jan Dhan Yojana ────────────────────────────────────────────
    Scheme(
        scheme_id="pm_jan_dhan",
        name="Pradhan Mantri Jan Dhan Yojana",
        ministry="Ministry of Finance",
        category=SchemeCategory.FINANCIAL_INCLUSION,
        description="Zero-balance bank account with RuPay debit card, insurance, and overdraft facility.",
        benefit_amount=10000,
        benefit_description="Overdraft up to ₹10,000 + ₹2 lakh accident insurance",
        eligibility_rules=[
            EligibilityRule(rule_id="jdy_1", rule_type=RuleType.AGE_MIN, condition=">=", value="10", description="Age ≥ 10"),
        ],
        required_documents=["aadhaar"],
        portal_url="https://pmjdy.gov.in",
        execution_tier=1,
        approval_rate=0.95,
        processing_days=7,
    ),

    # ── 5. Sukanya Samriddhi Yojana ──────────────────────────────────────
    Scheme(
        scheme_id="sukanya_samriddhi",
        name="Sukanya Samriddhi Yojana",
        ministry="Ministry of Finance",
        category=SchemeCategory.GIRL_CHILD,
        description="High-interest savings scheme for girl child education and marriage.",
        benefit_amount=250000,
        benefit_description="Tax-free returns at 8.2% p.a. (maturity at 21 years)",
        eligibility_rules=[
            EligibilityRule(rule_id="ssy_1", rule_type=RuleType.HAS_DAUGHTERS, condition="==", value="true", description="Must have at least one daughter"),
            EligibilityRule(rule_id="ssy_2", rule_type=RuleType.CUSTOM, condition="child_age_max", value="10", description="Daughter's age ≤ 10"),
        ],
        required_documents=["aadhaar", "birth_certificate", "bank_statement"],
        portal_url="https://www.india.gov.in/sukanya-samriddhi-yojana",
        execution_tier=2,
        approval_rate=0.90,
        processing_days=14,
        conflicts_with=["beti_bachao"],
    ),

    # ── 6. Beti Bachao Beti Padhao ──────────────────────────────────────
    Scheme(
        scheme_id="beti_bachao",
        name="Beti Bachao Beti Padhao",
        ministry="Ministry of Women & Child Development",
        category=SchemeCategory.GIRL_CHILD,
        description="Awareness and service delivery for protection and education of girl child.",
        benefit_amount=50000,
        benefit_description="Education and welfare grants for girl children",
        eligibility_rules=[
            EligibilityRule(rule_id="bb_1", rule_type=RuleType.HAS_DAUGHTERS, condition="==", value="true", description="Must have at least one daughter"),
        ],
        required_documents=["aadhaar", "birth_certificate", "income_certificate"],
        portal_url="https://wcd.nic.in/bbbp-schemes",
        execution_tier=2,
        approval_rate=0.75,
        processing_days=45,
        conflicts_with=["sukanya_samriddhi"],
    ),

    # ── 7. PM Matru Vandana Yojana ───────────────────────────────────────
    Scheme(
        scheme_id="pm_matru_vandana",
        name="Pradhan Mantri Matru Vandana Yojana",
        ministry="Ministry of Women & Child Development",
        category=SchemeCategory.MATERNITY,
        description="Cash incentive for first-time pregnant and lactating mothers.",
        benefit_amount=5000,
        benefit_description="₹5,000 in three installments during pregnancy",
        eligibility_rules=[
            EligibilityRule(rule_id="mv_1", rule_type=RuleType.GENDER, condition="==", value="female", description="Must be female"),
            EligibilityRule(rule_id="mv_2", rule_type=RuleType.PREGNANT, condition="==", value="true", description="Must be pregnant or lactating"),
            EligibilityRule(rule_id="mv_3", rule_type=RuleType.AGE_MIN, condition=">=", value="19", description="Age ≥ 19"),
        ],
        required_documents=["aadhaar", "bank_statement", "income_certificate"],
        portal_url="https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana",
        execution_tier=2,
        approval_rate=0.78,
        processing_days=30,
    ),

    # ── 8. National Social Assistance Programme (Old Age Pension) ────────
    Scheme(
        scheme_id="nsap_pension",
        name="Indira Gandhi National Old Age Pension",
        ministry="Ministry of Rural Development",
        category=SchemeCategory.PENSION,
        description="Monthly pension for BPL citizens aged 60+ (₹200–₹500/month).",
        benefit_amount=6000,
        benefit_description="₹200-500/month pension for elderly BPL citizens",
        eligibility_rules=[
            EligibilityRule(rule_id="nsap_1", rule_type=RuleType.AGE_MIN, condition=">=", value="60", description="Age ≥ 60"),
            EligibilityRule(rule_id="nsap_2", rule_type=RuleType.BPL, condition="==", value="true", description="Must belong to BPL household"),
        ],
        required_documents=["aadhaar", "bpl_card", "bank_statement", "income_certificate"],
        portal_url="https://nsap.nic.in",
        execution_tier=2,
        approval_rate=0.70,
        processing_days=60,
    ),

    # ── 9. Atal Pension Yojana ───────────────────────────────────────────
    Scheme(
        scheme_id="atal_pension",
        name="Atal Pension Yojana",
        ministry="Ministry of Finance",
        category=SchemeCategory.PENSION,
        description="Guaranteed minimum pension of ₹1,000–₹5,000 for unorganized sector workers.",
        benefit_amount=60000,
        benefit_description="₹1,000–₹5,000/month pension after 60 years of age",
        eligibility_rules=[
            EligibilityRule(rule_id="apy_1", rule_type=RuleType.AGE_MIN, condition=">=", value="18", description="Age ≥ 18"),
            EligibilityRule(rule_id="apy_2", rule_type=RuleType.AGE_MAX, condition="<=", value="40", description="Age ≤ 40"),
            EligibilityRule(rule_id="apy_3", rule_type=RuleType.INCOME_MAX, condition="<=", value="180000", description="Annual income ≤ ₹1.8 lakh (tax-exempt)"),
        ],
        required_documents=["aadhaar", "bank_statement"],
        portal_url="https://www.npscra.nsdl.co.in/scheme-details.php",
        execution_tier=1,
        approval_rate=0.88,
        processing_days=14,
    ),

    # ── 10. National Scholarship Portal ──────────────────────────────────
    Scheme(
        scheme_id="national_scholarship",
        name="National Scholarship Portal — Post-Matric Scholarship",
        ministry="Ministry of Social Justice",
        category=SchemeCategory.SCHOLARSHIP,
        description="Financial assistance for SC/ST/OBC/Minority students for post-matric education.",
        benefit_amount=36000,
        benefit_description="Tuition fee + maintenance allowance up to ₹36,000/year",
        eligibility_rules=[
            EligibilityRule(rule_id="nsp_1", rule_type=RuleType.CASTE, condition="in", value="sc,st,obc", description="Must be SC/ST/OBC"),
            EligibilityRule(rule_id="nsp_2", rule_type=RuleType.EDUCATION_MIN, condition=">=", value="higher_secondary", description="Completed higher secondary"),
            EligibilityRule(rule_id="nsp_3", rule_type=RuleType.INCOME_MAX, condition="<=", value="250000", description="Family income ≤ ₹2.5 lakh"),
        ],
        required_documents=["aadhaar", "caste_certificate", "income_certificate", "educational_certificate", "bank_statement"],
        portal_url="https://scholarships.gov.in",
        execution_tier=1,
        approval_rate=0.72,
        processing_days=45,
    ),

    # ── 11. Ayushman Bharat (PM-JAY) ─────────────────────────────────────
    Scheme(
        scheme_id="ayushman_bharat",
        name="Ayushman Bharat — PM Jan Arogya Yojana",
        ministry="Ministry of Health & Family Welfare",
        category=SchemeCategory.HEALTHCARE,
        description="Health insurance cover of ₹5 lakh per family per year for secondary and tertiary hospitalization.",
        benefit_amount=500000,
        benefit_description="₹5 lakh per family per year health cover",
        eligibility_rules=[
            EligibilityRule(rule_id="ab_1", rule_type=RuleType.BPL, condition="==", value="true", description="BPL or deprived household"),
            EligibilityRule(rule_id="ab_2", rule_type=RuleType.INCOME_MAX, condition="<=", value="300000", description="Annual income ≤ ₹3 lakh"),
        ],
        required_documents=["aadhaar", "ration_card", "income_certificate"],
        portal_url="https://pmjay.gov.in",
        execution_tier=1,
        approval_rate=0.82,
        processing_days=14,
    ),

    # ── 12. Mudra Loan (PMMY) ────────────────────────────────────────────
    Scheme(
        scheme_id="mudra_loan",
        name="Pradhan Mantri Mudra Yojana",
        ministry="Ministry of Finance",
        category=SchemeCategory.ENTREPRENEURSHIP,
        description="Collateral-free loans up to ₹10 lakh for micro/small enterprises.",
        benefit_amount=1000000,
        benefit_description="Loans: Shishu (≤₹50K), Kishore (≤₹5L), Tarun (≤₹10L)",
        eligibility_rules=[
            EligibilityRule(rule_id="mud_1", rule_type=RuleType.AGE_MIN, condition=">=", value="18", description="Age ≥ 18"),
            EligibilityRule(rule_id="mud_2", rule_type=RuleType.OCCUPATION, condition="in", value="self_employed,farmer", description="Self-employed or micro-enterprise"),
        ],
        required_documents=["aadhaar", "pan", "bank_statement", "income_certificate"],
        portal_url="https://www.mudra.org.in",
        execution_tier=2,
        approval_rate=0.68,
        processing_days=30,
    ),

    # ── 13. PM Disability Pension ────────────────────────────────────────
    Scheme(
        scheme_id="disability_pension",
        name="Indira Gandhi National Disability Pension",
        ministry="Ministry of Social Justice & Empowerment",
        category=SchemeCategory.DISABILITY,
        description="Monthly pension for severely disabled BPL citizens aged 18–79.",
        benefit_amount=3600,
        benefit_description="₹300/month pension for disabled BPL citizens",
        eligibility_rules=[
            EligibilityRule(rule_id="dp_1", rule_type=RuleType.DISABILITY, condition="==", value="true", description="Must have ≥80% disability"),
            EligibilityRule(rule_id="dp_2", rule_type=RuleType.AGE_MIN, condition=">=", value="18", description="Age ≥ 18"),
            EligibilityRule(rule_id="dp_3", rule_type=RuleType.AGE_MAX, condition="<=", value="79", description="Age ≤ 79"),
            EligibilityRule(rule_id="dp_4", rule_type=RuleType.BPL, condition="==", value="true", description="BPL household"),
        ],
        required_documents=["aadhaar", "disability_certificate", "bpl_card", "bank_statement"],
        portal_url="https://nsap.nic.in",
        execution_tier=2,
        approval_rate=0.72,
        processing_days=45,
    ),

    # ── 14. National Food Security Act (Ration Card) ─────────────────────
    Scheme(
        scheme_id="nfsa_ration",
        name="National Food Security Act — Subsidized Ration",
        ministry="Ministry of Consumer Affairs",
        category=SchemeCategory.FOOD_SECURITY,
        description="Subsidized food grains (rice ₹3/kg, wheat ₹2/kg) via PDS for BPL families.",
        benefit_amount=7200,
        benefit_description="5 kg/person/month at ₹1–₹3/kg (35 kg for Antyodaya)",
        eligibility_rules=[
            EligibilityRule(rule_id="nfsa_1", rule_type=RuleType.BPL, condition="==", value="true", description="BPL household"),
        ],
        required_documents=["aadhaar", "ration_card", "income_certificate"],
        portal_url="https://nfsa.gov.in",
        execution_tier=2,
        approval_rate=0.88,
        processing_days=30,
    ),

    # ── 15. Stand-Up India Scheme ────────────────────────────────────────
    Scheme(
        scheme_id="standup_india",
        name="Stand-Up India Scheme",
        ministry="Ministry of Finance",
        category=SchemeCategory.ENTREPRENEURSHIP,
        description="Bank loans ₹10 lakh–₹1 crore for SC/ST and women entrepreneurs for greenfield enterprises.",
        benefit_amount=10000000,
        benefit_description="Loans ₹10 lakh to ₹1 crore for greenfield enterprise",
        eligibility_rules=[
            EligibilityRule(rule_id="sui_1", rule_type=RuleType.AGE_MIN, condition=">=", value="18", description="Age ≥ 18"),
            EligibilityRule(rule_id="sui_2", rule_type=RuleType.CUSTOM, condition="sc_st_or_female", value="true", description="Must be SC/ST or female"),
        ],
        required_documents=["aadhaar", "pan", "caste_certificate", "bank_statement", "income_certificate"],
        portal_url="https://www.standupmitra.in",
        execution_tier=2,
        approval_rate=0.55,
        processing_days=60,
        depends_on=["pm_jan_dhan"],
    ),

    # ── 16. PM Fasal Bima Yojana ─────────────────────────────────────────
    Scheme(
        scheme_id="pm_fasal_bima",
        name="Pradhan Mantri Fasal Bima Yojana",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category=SchemeCategory.INSURANCE,
        description="Crop insurance at subsidized premiums for farmers against natural calamities.",
        benefit_amount=200000,
        benefit_description="Crop insurance cover up to ₹2 lakh with 2% premium",
        eligibility_rules=[
            EligibilityRule(rule_id="pfb_1", rule_type=RuleType.OCCUPATION, condition="==", value="farmer", description="Must be a farmer"),
        ],
        required_documents=["aadhaar", "bank_statement", "income_certificate"],
        portal_url="https://pmfby.gov.in",
        execution_tier=1,
        approval_rate=0.80,
        processing_days=21,
        depends_on=["pm_kisan"],
    ),
]

# Quick lookup by scheme_id
SCHEME_MAP: dict[str, Scheme] = {s.scheme_id: s for s in SCHEMES}
