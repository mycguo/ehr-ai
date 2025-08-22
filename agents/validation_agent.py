from rag.vector_store import search_vector_store

def check_payer_rules(inputs: dict) -> dict:
    bundle = inputs["bundle"]
    payer = "Aetna"

    query = f"{bundle['cpt']} {bundle['procedures']} modifier {payer}"
    docs = search_vector_store(query)

    needs_modifier = any("CO-197" in doc for doc in docs)
    return {
        "requires_modifier": needs_modifier,
        "justification": "Modifier 25 required due to bundling rules (CO-197)" if needs_modifier else "",
        "evidence": docs,
        "bundle": bundle,
        "context": inputs["context"]
    }
