from rag.vector_store import client

def bootstrap_vector_store():
    coll = client.get_or_create_collection("payer_knowledge")

    with open("data/icd10.txt") as f:
        for line in f:
            coll.add(documents=[line.strip()], metadatas=[{"type": "icd"}], ids=[f"icd-{hash(line)}"])

    with open("data/cpt.txt") as f:
        for line in f:
            coll.add(documents=[line.strip()], metadatas=[{"type": "cpt"}], ids=[f"cpt-{hash(line)}"])

    with open("data/payer_rules.txt") as f:
        for line in f:
            coll.add(documents=[line.strip()], metadatas=[{"type": "payer_rule"}], ids=[f"payer-{hash(line)}"])
