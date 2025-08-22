# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered agentic billing system that automates medical billing claim generation from SOAP notes. The system uses a multi-agent architecture orchestrated by LangGraph, with natural language processing powered by Google's Gemini Pro model and retrieval-augmented generation (RAG) via ChromaDB.

## Architecture

The system follows a microservices architecture with agent-based workflows:

- **FastAPI REST API** (`api.py`): Single endpoint `/generate-claim` that accepts SOAP notes
- **LangGraph Workflow** (`langgraph/billing_graph.py`): Orchestrates 5 specialized agents in sequence
- **AI Agents** (`agents/`): Specialized processors for each stage of claim generation
- **Vector Store** (`rag/`): ChromaDB-based RAG system for medical codes and payer rules
- **Denial Risk Model** (`score-denial-risk-model/`): Separate LightGBM-based ML service for claim risk scoring

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

### Docker Development
```bash
# Build and start all services
docker-compose up --build

# Seed vector store (required first time)
docker-compose run billing-agent python main.py

# Run specific service only
docker-compose up chroma  # ChromaDB only
```

### Testing
```bash
# Run all tests
pytest -s

# Run specific test file
pytest tests/test_billing_graph.py -s

# Test the API endpoint
curl -X POST http://localhost:8000/generate-claim \
  -H "Content-Type: application/json" \
  -d '{"soap_note": "Patient presented for 25-minute follow-up for diabetes management. Ordered urinalysis. Reports increased thirst."}'
```

### Denial Risk Model
```bash
# Navigate to the model directory
cd score-denial-risk-model

# Install model dependencies
pip install -r requirements

# Process training data
cd pre-processor && python data_processor.py

# Train the model
cd ../model && python train_denial_risk_model.py

# Start the risk scoring API
cd ../app && uvicorn app:app --reload
```

## Agent Workflow Pipeline

The LangGraph workflow processes claims through 5 sequential agents:

1. **EMR Extractor** (`agents/emr_extractor.py`): Parses SOAP notes into structured `EncounterContext`
2. **Code Agent** (`agents/code_agent.py`): Converts clinical data to CPT/ICD-10/modifier bundles
3. **Validation Agent** (`agents/validation_agent.py`): Validates against payer rules via RAG
4. **Modifier Agent** (`agents/modifier_agent.py`): Applies risk-based modifiers
5. **EDI Formatter** (`agents/edi_formatter.py`): Generates final EDI X12 claim format

## Configuration Requirements

### Environment Variables
Required for Google Cloud Vertex AI integration:
```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=your-gcp-location
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Vector Store Data
The RAG system requires seeding with medical knowledge:
- `data/cpt.txt`: CPT codes and descriptions
- `data/icd10.txt`: ICD-10 codes and descriptions  
- `data/payer_rules.txt`: Payer-specific billing rules

## Key Technical Patterns

### Agent State Management
All agents operate on a shared `AgentState` TypedDict that flows through the LangGraph pipeline:
```python
class AgentState(TypedDict):
    soap_note: str
    context: Optional[dict]
    bundle: Optional[dict]
    requires_modifier: Optional[bool]
    justification: Optional[str]
    evidence: Optional[List[str]]
    edi: Optional[str]
```

### RAG Implementation
The system uses ChromaDB for semantic search across medical codes and payer policies:
- Vector embeddings for CPT, ICD-10, and payer rule documents
- Query-time retrieval provides context to AI agents
- Runs on port 8001 in Docker setup

### Gemini Integration
Google's Vertex AI Gemini 2.5 Pro model handles natural language tasks:
- Structured data extraction with Pydantic schemas
- Function calling for medical code generation
- Chain-of-thought reasoning for validation decisions

## File Structure Context

```
ehr-ai/
├── agents/                    # Specialized AI agents
├── langgraph/                 # Workflow orchestration
├── llm/                       # LLM integration layer
├── rag/                       # Vector store and document loading
├── data/                      # Medical codes and payer rules
├── score-denial-risk-model/   # Separate ML risk scoring service
├── tests/                     # Test suite
├── api.py                     # Main FastAPI application
├── main.py                    # Vector store bootstrap script
└── docker-compose.yml         # Multi-service orchestration
```

## Development Notes

- The system is designed with human-in-the-loop patterns for high-value/ambiguous claims
- All agents provide structured outputs with rationale for decisions
- ChromaDB requires initial seeding via `python main.py` before first use
- The denial risk model is a separate service that can be integrated with the main workflow
- Agent prompts include retrieval context from the vector store for accurate medical coding