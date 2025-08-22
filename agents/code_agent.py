import json
import re
import json
import re
from llm.gemini_llm import ask_gemini
from rag.vector_store import search_vector_store

def convert_to_CPT_ICD_modifier_bundle(inputs: dict) -> dict:
    context = inputs["context"]

    # Retrieve relevant CPT and ICD-10 codes from the vector store
    cpt_query = f"CPT codes for {context['visit_type']} {context['duration']}"
    icd_query = f"ICD-10 codes for {context['diagnosis']} {context['symptoms']}"

    relevant_cpt = search_vector_store(cpt_query)
    relevant_icd = search_vector_store(icd_query)

    prompt = f"""You are a medical coder. Suggest CPT, ICD-10, and modifier codes based on the following patient encounter details and relevant medical codes:

Patient Encounter Details:
Visit type: {context['visit_type']}
Duration: {context['duration']}
Diagnoses: {context['diagnosis']}
Symptoms: {context['symptoms']}
Ordered tests: {context['ordered_tests']}

Relevant CPT Codes:
{relevant_cpt}

Relevant ICD-10 Codes:
{relevant_icd}

Return as JSON:
{{
  "cpt": "<primary CPT>", 
  "icd": ["<ICD list>"], 
  "modifiers": [], 
  "procedures": ["<CPTs>"]
}}
"""
    response_text = ask_gemini(prompt)
    print(f"CODE AGENT --- LLM RESPONSE: {response_text}")
    
    # Use regex to find the JSON block
    json_match = re.search(r"```json\n(.*?)```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Fallback if no markdown block is found
        json_str = response_text

    try:
        codes = json.loads(json_str)
    except json.JSONDecodeError:
        # Handle cases where the JSON is still invalid
        codes = {}

    return {"context": context, "bundle": codes}
