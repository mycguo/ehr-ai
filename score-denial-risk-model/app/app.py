import os
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import lightgbm as lgb

# Load model and encoder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
clf = joblib.load(os.path.join(project_root, "denial_risk_model_lgbm.pkl"))
le = joblib.load(os.path.join(project_root, "label_encoder_icd_ccs_id.pkl"))
ccs_df = pd.read_csv(os.path.join(project_root, "data", "ccsr_icd10cm_2025_v1.csv"), dtype=str)
ccs_df = ccs_df.rename(columns={
    "'ICD-10-CM CODE'": "icd10",
    "'CCSR CATEGORY 1'": "ccs_category"
})
ccs_df["icd10"] = ccs_df["icd10"].str.replace(".", "").str.upper().str.strip()

# Setup FastAPI
app = FastAPI()

# Define request schema
class ClaimInput(BaseModel):
    cpt: str
    payer: str
    pos: str
    duration: int
    icd_count: int
    modifier_count: int
    has_modifier_25: int
    procedures_count: int
    past_denial_rate: float
    primary_icd: str

@app.post("/predict")
def predict_denial(claim: ClaimInput):
    try:
        # Normalize ICD
        primary_icd = claim.primary_icd.replace(".", "").upper().strip()
        match = ccs_df[ccs_df["icd10"] == primary_icd]
        if match.empty:
            ccs_id = "Unknown"
        else:
            ccs_id = match.iloc[0]["ccs_category"]

        # Encode CCS ID
        if ccs_id not in le.classes_:
            ccs_id = "Unknown"
        icd_ccs_id_encoded = le.transform([ccs_id])[0]

        # Build feature vector
        input_row = {
            "cpt": claim.cpt,
            "payer": claim.payer,
            "pos": claim.pos,
            "duration": claim.duration,
            "icd_count": claim.icd_count,
            "modifier_count": claim.modifier_count,
            "has_modifier_25": claim.has_modifier_25,
            "procedures_count": claim.procedures_count,
            "past_denial_rate": claim.past_denial_rate,
            "icd_ccs_id_encoded": icd_ccs_id_encoded,
        }

        X = pd.DataFrame([input_row])
        probability = clf.predict_proba(X)[0][1]
        predicted = int(probability > 0.5)

        return {
            "risk_score": round(probability, 4),
            "predicted": predicted,
            "icd_ccs_id": ccs_id
        }

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
