import re
import tldextract
from sqlalchemy.orm import Session
from models import ScamPattern

FREE_EMAIL_DOMAINS = {
    "gmail.com","yahoo.com","outlook.com","hotmail.com","proton.me","protonmail.com",
    "icloud.com","yandex.com","zoho.com","gmx.com","mail.com","aol.com","rediffmail.com"
}

TRUSTED_POSTING_DOMAINS = {
    "linkedin.com","internshala.com","naukri.com","glassdoor.com","indeed.com","wellfound.com","angel.co"
}

SUSPICIOUS_TLDS = {"xyz","top","work","click","fit","shop","link","cam","site","info"}

def seed_default_patterns(db: Session):
    if db.query(ScamPattern).count() > 0:
        return
    defaults = [
        ("registration fee", "Asks for an upfront registration fee.", -25, "fee"),
        ("security deposit", "Asks for a refundable deposit for internship.", -25, "fee"),
        ("certificate fee", "Charges for certificate/completion letter.", -20, "fee"),
        ("training fee", "Mandatory paid training before internship.", -20, "fee"),
        ("guaranteed placement", "Unrealistic guarantee of job/placement.", -20, "promise"),
        ("pay to apply", "Payment required to apply.", -25, "fee"),
        ("dm for details", "Vague DM-only instructions; no official channel.", -10, "vague"),
        ("telegram only", "Only Telegram contact; no official email/site.", -15, "vague"),
        ("whatsapp only", "Only WhatsApp contact; no official email/site.", -15, "vague"),
        ("no stipend", "Explicitly mentions no stipend.", -5, "unpaid"),
        ("unpaid internship", "Unpaid internship.", -5, "unpaid"),
    ]
    for kw, desc, w, tag in defaults:
        db.add(ScamPattern(keyword=kw, description=desc, weight=w, tag=tag))
    db.commit()

def extract_domain(value: str | None) -> str | None:
    if not value:
        return None
    if "@" in value:
        value = value.split("@", 1)[1]
    ext = tldextract.extract(value)
    if not ext.domain:
        return None
    return f"{ext.domain}.{ext.suffix}".lower() if ext.suffix else ext.domain.lower()

def detect_paid_status(text: str) -> bool | None:
    if not text:
        return None
    t = text.lower()
    unpaid = ["unpaid", "volunteer", "no stipend"]
    paid = ["stipend", "per month", "salary", "ctc", "paid internship", "₹", "rs.", "package"]
    if any(m in t for m in unpaid):
        return False
    if any(m in t for m in paid):
        return True
    return None

def clamp(n: int, low: int=0, high: int=100) -> int:
    return max(low, min(high, n))

def verify_internship(data: dict, db: Session) -> dict:
    link = (data.get("link") or "").strip()
    description = (data.get("description") or "").strip()
    email = (data.get("email") or "").strip()

    explanations: list[str] = []
    score = 50  # neutral base

    # 1) Email check
    if email:
        dom = extract_domain(email)
        if dom in FREE_EMAIL_DOMAINS:
            score -= 15
            explanations.append(f"Contact email uses free provider ({dom}).")
        elif dom:
            score += 5
            explanations.append(f"Contact email domain looks corporate ({dom}).")
    else:
        explanations.append("No contact email provided.")

    # 2) Link checks
    link_dom = extract_domain(link) if link else None
    if link_dom:
        if any(td in link_dom for td in TRUSTED_POSTING_DOMAINS):
            score += 10
            explanations.append(f"Posted on a known platform ({link_dom}).")
        tld = link_dom.split(".")[-1]
        if tld in SUSPICIOUS_TLDS:
            score -= 10
            explanations.append(f"Suspicious top-level domain (.{tld}).")
        if re.search(r"/[A-Za-z0-9]{20,}", link):
            score -= 5
            explanations.append("URL contains long random-looking path.")
    else:
        explanations.append("No link provided; relying on text analysis.")

    # 3) Keyword patterns from DB
    if description:
        patterns = db.query(ScamPattern).all()
        matched_any = False
        t = description.lower()
        for p in patterns:
            if p.keyword in t:
                matched_any = True
                score += p.weight
                explanations.append(p.description or f"Matched pattern: {p.keyword}")
        if not matched_any:
            score += 5
            explanations.append("No scam phrases detected in description.")
    else:
        score -= 10
        explanations.append("No description text provided.")

    # 4) Paid/unpaid
    paid = detect_paid_status(description)

    # 5) Finalize
    score = clamp(int(score))
    if score >= 75:
        status = "Real"
    elif score <= 40:
        status = "Fake"
    else:
        status = "Suspicious"

    # dedupe explanations
    seen, cleaned = set(), []
    for e in explanations:
        if e not in seen:
            cleaned.append(e); seen.add(e)

    return {"status": status, "paid": paid, "credibility": score, "explanations": cleaned}
