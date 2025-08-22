import json
import re
from llm.gemini_llm import ask_gemini

def apply_risk_modifiers(inputs: dict):
    bundle = inputs["bundle"]
    context = inputs["context"]
    evidence = inputs["evidence"]

    prompt = f"""You are a medical coding expert. Based on the following CPT/ICD bundle, patient context, and payer rules evidence, determine if any modifiers need to be applied to the CPT codes. If so, list them.

CPT/ICD Bundle:
{json.dumps(bundle, indent=2)}

Patient Context:
Visit Type: {context['visit_type']}
Duration: {context['duration']}
Diagnoses: {context['diagnosis']}
Symptoms: {context['symptoms']}
Ordered Tests: {context['ordered_tests']}
Provider: {context['provider']}
POS: {context['pos']}

Payer Rules Evidence:
{evidence}

Return only a JSON object with a single key 'modifiers' which is a list of strings. If no modifiers are needed, return an empty list.
Example: {{"modifiers": ["25", "59"]}}
"""

    response_text = ask_gemini(prompt)
    print(f"MODIFIER AGENT --- LLM Response: {response_text}")
    
    # Use regex to find the JSON block
    json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Fallback if no markdown block is found
        json_str = response_text

    try:
        llm_modifiers = json.loads(json_str).get("modifiers", [])
    except json.JSONDecodeError:
        llm_modifiers = []

    # Combine existing modifiers with LLM-suggested modifiers (if any)
    # Ensure uniqueness if needed, though LLM should ideally provide unique ones
    bundle["modifiers"].extend(llm_modifiers)
    bundle["modifiers"] = list(set(bundle["modifiers"]))

    return {"context": context, "bundle": bundle}
