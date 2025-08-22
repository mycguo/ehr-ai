# Agentic Billing System: Technical Design

## 1. Overview

This document outlines the technical design of the Agentic Billing System, a solution built to automate the generation of medical billing claims from clinical SOAP notes. The system leverages a multi-agent architecture orchestrated by LangGraph, with natural language understanding powered by Google's Gemini Pro large language model. It ensures accuracy and compliance by referencing a vector store populated with CPT codes, ICD-10 codes, and payer-specific rules.

## 2. System Architecture

The system is composed of several key components:

- **FastAPI REST API**: Exposes an endpoint for submitting SOAP notes and receiving generated EDI X12 claims.
- **LangGraph Workflow**: Orchestrates a sequence of specialized agents to process the billing claim.
- **Gemini Pro LLM**: Provides the core natural language processing capabilities for data extraction and code generation.
- **ChromaDB Vector Store**: A retrieval-augmented generation (RAG) database that stores and provides fast access to medical coding and payer rule information.
- **Dockerized Environment**: Ensures consistent deployment and scalability.

## 3. File & Folder Hierarchy

```
agentic-billing/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
├── api.py
├── agents/
│   ├── emr_extractor.py
│   ├── code_agent.py
│   ├── validation_agent.py
│   ├── modifier_agent.py
│   └── edi_formatter.py
├── langgraph/
│   └── billing_graph.py
├── llm/
│   └── gemini_llm.py
├── rag/
│   ├── vector_store.py
│   └── document_loader.py
├── data/
│   ├── icd10.txt
│   ├── cpt.txt
│   └── payer_rules.txt
```

## 4. Core Components

### 4.1. `api.py` - REST Interface

The application's entry point is a FastAPI server that exposes a single endpoint:

- **`POST /generate-claim`**: Accepts a JSON payload containing a `soap_note` and returns a generated EDI X12 claim.

```python
from fastapi import FastAPI, Request
from langgraph.billing_graph import build_graph

app = FastAPI()
graph = build_graph()

@app.post("/generate-claim")
async def generate_claim(request: Request):
    body = await request.json()
    result = graph.invoke({
        "soap_note": body["soap_note"]
    })
    return result
```

### 4.2. `langgraph/billing_graph.py` - Agentic Workflow

The core logic is defined in a LangGraph state machine that coordinates the agents:

1.  **`extract`**: The `emr_extractor` agent parses the SOAP note.
2.  **`convert`**: The `code_agent` converts clinical data to billing codes.
3.  **`validate`**: The `validation_agent` checks for payer-specific rules.
4.  **`modify`**: The `modifier_agent` applies any necessary modifiers.
5.  **`format`**: The `edi_formatter` generates the final EDI X12 claim.

```python
from langgraph.graph import StateGraph
from agents import emr_extractor, code_agent, validation_agent, modifier_agent, edi_formatter

def build_graph():
    graph = StateGraph()
    graph.add_node("extract", emr_extractor.review_and_extract_emr_data)
    graph.add_node("convert", code_agent.convert_to_CPT_ICD_modifier_bundle)
    graph.add_node("validate", validation_agent.check_payer_rules)
    graph.add_node("modify", modifier_agent.apply_risk_modifiers)
    graph.add_node("format", edi_formatter.format_to_edi_x12)

    graph.set_entry_node("extract")
    graph.add_edge("extract", "convert")
    graph.add_edge("convert", "validate")
    graph.add_edge("validate", "modify")
    graph.add_edge("modify", "format")
    graph.set_finish_node("format")

    return graph.compile()
```

### 4.3. `llm/gemini_llm.py` - Language Model Integration

This module provides a simple interface to the Gemini Pro model.

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-pro")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
```

### 4.4. `rag/` - Retrieval-Augmented Generation

The RAG system consists of a vector store and a document loader.

- **`vector_store.py`**: Manages interactions with the ChromaDB client.
- **`document_loader.py`**: Seeds the vector store with data from the `data/` directory.

## 5. Agents

### 5.1. `agents/emr_extractor.py`

Extracts structured clinical information from the unstructured SOAP note.

### 5.2. `agents/code_agent.py`

Takes the structured clinical data and generates a "bundle" of CPT, ICD-10, and modifier codes.

### 5.3. `agents/validation_agent.py`

Queries the vector store to determine if any payer-specific rules apply to the generated code bundle.

### 5.4. `agents/modifier_agent.py`

Applies modifiers (e.g., "25") to the code bundle based on the validation step.

### 5.5. `agents/edi_formatter.py`

Formats the final, validated code bundle into a standard EDI X12 string.

## 6. Data

The `data/` directory contains the raw data used to populate the vector store:

- `cpt.txt`: A list of CPT codes and descriptions.
- `icd10.txt`: A list of ICD-10 codes and descriptions.
- `payer_rules.txt`: A list of payer-specific billing rules.

## 7. Deployment

The application is designed to be deployed using Docker and Docker Compose.

- **`Dockerfile`**: Defines the container image for the billing agent service.
- **`docker-compose.yml`**: Orchestrates the `billing-agent` and `chroma` database services.

## 8. Usage

To run the system:

1.  **Seed the vector store**:
    ```bash
    python main.py
    ```
2.  **Start the services**:
    ```bash
    docker-compose up -d
    ```
3.  **Submit a claim**:
    ```bash
    curl -X POST http://localhost:8000/generate-claim \
      -H "Content-Type: application/json" \
      -d '{
        "soap_note": "Patient presented for 25-minute follow-up for diabetes management. Ordered urinalysis. Reports increased thirst."
      }'
    ```