from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import re

# 1. Request Data Structure Definition
class JobRequest(BaseModel):
    description: str

# 2. FastAPI Application Instance Initialization
app = FastAPI(title="JobShield AI Backend", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Secure Machine Learning Model Loading
try:
    model = joblib.load("model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    print("🧠 JobShield AI models successfully loaded into memory.")
except Exception as e:
    print(f"❌ Error loading model files: {e}")

# 4. Helper Analysis Functions (Advanced Heuristics Layer)
def parse_maximum_salary(text_lowercase: str) -> int:
    """
    Parses compensation values from text string and standardizes them into annualized figures.
    Handles formats like: $150,000, $120k, $45/hour
    """
    # Look for standard dollar formats or 'k' notation (e.g., $140,000, $140k)
    salary_matches = re.findall(r'\$?(\d{2,3}),?(\d{3})?|\$?(\d{2,3})[kK]', text_lowercase)
    salary_vals = []
    
    for match in salary_matches:
        val = match[0] or match[2]
        if val:
            numeric_val = int(val) * 1000 if int(val) < 1000 else int(val)
            salary_vals.append(numeric_val)
            
    # If no annual salary found, check for hourly rate indicators (e.g., $35 - $45 / hour)
    if not salary_vals:
        hourly_matches = re.findall(r'\$?(\d{2,2})\.?\d*?\s*/?\s*(?:hr|hour|bucks)', text_lowercase)
        if hourly_matches:
            # Approximate calculation: hourly wage * 2000 hours per year
            salary_vals = [int(h) * 2000 for h in hourly_matches]
            
    return max(salary_vals) if salary_vals else 0


# 5. Core API Endpoints
@app.get("/")
def home():
    return {"status": "online", "system": "JobShield AI API Engine"}

@app.post("/analyze")
def analyze_job(job: JobRequest):
    raw_text = job.description
    text_lowercase = raw_text.lower()

    # --- Phase 1: Machine Learning Predictive Pipeline ---
    X = vectorizer.transform([raw_text])
    probabilities = model.predict_proba(X)[0]

    genuine_prob = round(probabilities[0] * 100, 2)
    fake_prob = round(probabilities[1] * 100, 2)

    # --- Phase 2: Heuristic Scam & Vulnerability Detection ---
    risk_score = 0
    detected_flags = []

    # Indicator Group A: Direct Financial Extortion Patterns
    high_risk_phrases = [
        "registration fee", "training fee", "certification fee",
        "security deposit", "processing fee", "assessment fee",
        "joining fee", "enrollment fee", "assessment processing charge",
        "processing charge", "refundable fee", "refundable amount",
        "test slot fee", "confirm your slot", "pay to attend",
        "payment required", "telegram", "whatsapp", "google form",
        "provide a check to purchase", "purchase your home office", 
        "buy equipment", "approved vendor", "check to buy", 
        "funds for equipment", "shipping vendor"
    ]

    for phrase in high_risk_phrases:
        if phrase in text_lowercase:
            risk_score += 50
            detected_flags.append(f"Found dynamic payment risk pattern: '{phrase}'")

    refund_phrases = ["refundable", "will be refunded", "reimbursed", "returned after"]
    for phrase in refund_phrases:
        if phrase in text_lowercase:
            risk_score += 15
            detected_flags.append(f"Detected suspicious reassurance: '{phrase}'")

    if ("fee" in text_lowercase or "charge" in text_lowercase) and ("refund" in text_lowercase or "refundable" in text_lowercase):
        risk_score += 50
        detected_flags.append("High match pattern: Mandatory transaction paired with reimbursement claims.")

    # Indicator Group B: Structural Data Logic Anomaly
    senior_keywords = ['senior', 'lead', 'principal', 'director', 'manager']
    is_senior = any(keyword in text_lowercase for keyword in senior_keywords)
    
    # Improved regex to handle "0 to 1", "1+", "3-5", "0-1" variations cleanly
    exp_match = re.search(r'(\d+)\s*(?:\+|–|-|to)\s*(\d*)\s*years?', text_lowercase)
    min_exp = int(exp_match.group(1)) if exp_match else None
    max_salary = parse_maximum_salary(text_lowercase)

    # If title says "Senior/Lead" but experience is entry-level
    if is_senior and min_exp is not None and min_exp <= 1:
        risk_score += 40
        detected_flags.append(f"Structural Anomaly: Position claims seniority title but requires only {min_exp} year(s) of experience.")

    # LOWERED THRESHOLD: If salary is > $80,000 ($40+/hr) but experience required is <= 1 year
    if max_salary >= 80000 and min_exp is not None and min_exp <= 1:
        risk_score += 45  # Increased penalty to ensure it hits the 40 threshold alone
        detected_flags.append(f"Economic Incongruity: Extracted high-tier compensation (${max_salary:,}/yr) paired with entry-level experience requirements.")

    # Indicator Group C: High Entropy Cross-Domain Keyword Assessment
    tech_domains = {
        "Cloud/DevOps": ["aws", "gcp", "azure", "lambda", "vertex ai", "cloud-native"],
        "Robotics/Embedded": ["ros 2", "ros2", "wheeled robot", "telemetry", "simulation"],
        "RPA/Automation": ["uipath", "orchestrator", "ui automation", "data manipulation"],
        "Quantum": ["quantum computing", "trapped ions", "superconducting circuits"]
    }
    
    matched_domains = []
    for domain, keywords in tech_domains.items():
        if any(keyword in text_lowercase for keyword in keywords):
            matched_domains.append(domain)
            
    if len(matched_domains) >= 3:
        risk_score += 45
        detected_flags.append(f"Entropy Anomaly: Highly contradictory skill mix spanning unrelated specialized fields ({', '.join(matched_domains)}).")

    # --- Phase 3: Hybrid Determination Strategy Engine ---
    reasons = []
    
    if risk_score >= 40:
        result = "Fake"
        confidence = round(max(90.0, fake_prob), 2)
        reasons = [
            "Critical structural logic or exploitation triggers detected.",
            "This posting contains contradictory requirements or patterns linked to deceptive listings."
        ] + detected_flags
    else:
        # Production Confidence Calibration for verified listings
        if len(detected_flags) == 0:
            base_confidence = genuine_prob if genuine_prob > fake_prob else (100 - fake_prob)
            calibrated_confidence = 85.0 + ((base_confidence - 50.0) / 50.0) * 13.0
            
            result = "Genuine"
            confidence = round(calibrated_confidence, 2)
            reasons = [
                "The posting features typical corporate and standard recruitment syntax.",
                "No upfront financial criteria, structural logic flaws, or unverified platforms were detected."
            ]
        else:
            if genuine_prob >= 70:
                result = "Genuine"
                confidence = genuine_prob
                reasons = [
                    "The posting matches professional templates, but proceed with standard application channels."
                ] + detected_flags
            elif fake_prob >= 70:
                result = "Fake"
                confidence = fake_prob
                reasons = [
                    "The semantic architecture correlates heavily with documented employment scams."
                ] + detected_flags
            else:
                result = "Suspicious"
                confidence = max(genuine_prob, fake_prob)
                reasons = [
                    "The description contains mixed language signals. Verify the employer independently."
                ] + detected_flags

    return {
        "prediction": result,
        "confidence": round(confidence, 2),
        "risk_score": risk_score,
        "reasons": reasons
    }