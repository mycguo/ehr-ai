import unittest
import sys
import os
import chromadb
from dotenv import load_dotenv


# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Automatically load .env before any tests run
load_dotenv()

from langgraph.billing_graph import build_graph

class TestBillingGraph(unittest.TestCase):
    def setUp(self):
        # Use an in-memory ChromaDB for testing
        self.client = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.client.get_or_create_collection("test_payer_knowledge")
        self.bootstrap_vector_store()
        self.graph = build_graph()


    def bootstrap_vector_store(self):
        coll = self.client.get_or_create_collection("payer_knowledge")

        with open("data/icd10.txt") as f:
            for line in f:
                coll.add(documents=[line.strip()], metadatas=[{"type": "icd"}], ids=[f"icd-{hash(line)}"])

        with open("data/cpt.txt") as f:
            for line in f:
                coll.add(documents=[line.strip()], metadatas=[{"type": "cpt"}], ids=[f"cpt-{hash(line)}"])

        with open("data/payer_rules.txt") as f:
            for line in f:
                coll.add(documents=[line.strip()], metadatas=[{"type": "payer_rule"}], ids=[f"payer-{hash(line)}"])


    def test_integration_billing_graph(self):
        # Load the SOAP note from the file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        soap_note_path = os.path.abspath(os.path.join(current_dir, '..', 'soap_note_test_ensure.txt'))
        with open(soap_note_path) as f:
            soap_note_content = f.read()

        # Prepare the initial state
        initial_state = {
            "soap_note": soap_note_content
        }

        # Invoke the graph
        final_state = self.graph.invoke(initial_state)

        print("Final State:", final_state)

        # Add assertions to verify the final state
        self.assertIsNotNone(final_state)
        self.assertIn("edi", final_state)
        self.assertIsNotNone(final_state["edi"])
        self.assertTrue(len(final_state["edi"]) > 0)

    def tearDown(self):
        # Clean up the test collection
        self.client.delete_collection("test_payer_knowledge")

if __name__ == '__main__':
    unittest.main()
