import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection("payer_knowledge")

def search_vector_store(query):
    results = collection.query(query_texts=[query], n_results=3)
    return results["documents"][0]

def query_emr_context(note):
    results = collection.query(query_texts=[note], n_results=3)
    return "\n".join(results["documents"][0])
