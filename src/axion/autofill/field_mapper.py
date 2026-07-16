"""Conservative browser/UI field classification."""
from __future__ import annotations
import re

PROHIBITED = ("password","passcode","otp","one time","verification code","cvv","cvc","card number","credit card","expiry","expiration","bank","account number","security answer","signature","payment")
SENSITIVE = {"phone","date_of_birth","address_line1","address_line2","postal_code","aadhaar","pan"}
RULES = [
 ("full_name",("full name","your name","applicant name")), ("first_name",("first name","given name")), ("last_name",("last name","surname")),
 ("email",("email","e-mail")), ("phone",("phone","mobile","telephone")), ("address_line1",("address","street")), ("city",("city","town")),
 ("state",("state","province")), ("postal_code",("postal","postcode","zip")), ("country",("country",)), ("college",("college","university")),
 ("course",("course","degree","program")), ("github",("github",)), ("linkedin",("linkedin",)), ("portfolio",("portfolio","website")),
 ("date_of_birth",("date of birth","dob","birth date")), ("aadhaar",("aadhaar","aadhar")), ("pan",("pan number","pan card")),
]
def field_text(field: dict) -> str:
    raw = " ".join(str(field.get(k,"")) for k in ("label","name","id","placeholder","autocomplete","type")).casefold()
    return re.sub(r"[^a-z0-9]+", " ", raw)
def is_prohibited(field: dict) -> bool:
    text=field_text(field)
    return str(field.get("type","")).casefold()=="password" or any(re.search(r"\b"+re.escape(x)+r"\b",text) for x in PROHIBITED)
def map_field(field: dict) -> dict:
    if is_prohibited(field): return {"profile_field":None,"status":"blocked","reason":"prohibited field"}
    text=field_text(field)
    for profile,terms in RULES:
        if any(term in text for term in terms): return {"profile_field":profile,"status":"sensitive" if profile in SENSITIVE else "safe","reason":f"matched {profile}"}
    return {"profile_field":None,"status":"unknown","reason":"no safe mapping"}
UPLOAD_RULES={"resume":("resume","cv"),"certificate":("certificate",),"marksheet":("marksheet","mark sheet"),"profile_photo":("profile photo","photograph"),"aadhaar":("aadhaar","aadhar","identity document"),"pan":("pan",),"portfolio":("portfolio",),"cover_letter":("cover letter",)}
def document_label(text: str) -> str | None:
    value=text.casefold()
    return next((label for label,terms in UPLOAD_RULES.items() if any(t in value for t in terms)),None)
