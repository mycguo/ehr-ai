from langchain_core.pydantic_v1 import BaseModel, Field
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from rag.vector_store import query_emr_context
import os


# Define the data structure for the extracted information using Pydantic
class EncounterContext(BaseModel):
    """Structured data extracted from a medical SOAP note."""
    visit_type: str = Field(..., description="The type of visit, e.g., 'follow-up', 'new patient'.")
    duration: str = Field(..., description="The duration of the visit, e.g., '25 minutes'.")
    diagnosis: list[str] = Field(..., description="A list of diagnoses mentioned.")
    symptoms: list[str] = Field(..., description="A list of symptoms reported by the patient.")
    ordered_tests: list[str] = Field(..., description="A list of any tests that were ordered.")
    provider: str = Field(..., description="The name of the healthcare provider.")
    pos: str = Field(..., description="The place of service, e.g., 'office', 'outpatient hospital'.")


# Function declaration for Vertex AI Tool
function_declaration = FunctionDeclaration(
    name="extract_encounter_context",
    description="Extracts structured encounter context from a SOAP note.",
    parameters=EncounterContext.schema()
)

# Create the tool
encounter_tool = Tool(function_declarations=[function_declaration])

def extract_encounter_context(encounter: EncounterContext):
    """Extracts encounter context from a SOAP note."""
    return encounter

def review_and_extract_emr_data(inputs: dict) -> dict:
    soap_note = inputs.get("soap_note", "")
    emr_fields = query_emr_context(soap_note)

    # Define the tool + model
    model = GenerativeModel(
        model_name="gemini-2.5-pro",
        tools=[encounter_tool]
    )

    prompt = f"""
    You are an expert medical billing AI.

    Analyze the following SOAP note and EMR context, then use the available tool
    to extract the required information.

    SOAP Note:
    {soap_note}

    EMR Context:
    {emr_fields}
    """

    response = model.generate_content(prompt)
    print(f"EMR AGENT --- LLM Response: {response}")

    try:
        tool_call = response.candidates[0].content.parts[0].function_call
        if tool_call.name == "extract_encounter_context":
            args = {key: value for key, value in tool_call.args.items()}
            return {"context": args}
    except (IndexError, AttributeError) as e:
        print(f"Error extracting tool call: {e}")
        print(f"LLM Response: {response}")
        return {"context": {}}

    return {"context": {}}
