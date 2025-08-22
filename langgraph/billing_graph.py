from langgraph.graph import StateGraph
from agents import emr_extractor, code_agent, validation_agent, modifier_agent, edi_formatter
from typing import TypedDict, List, Optional

# Define the state schema
class AgentState(TypedDict):
    soap_note: str
    context: Optional[dict]
    bundle: Optional[dict]
    requires_modifier: Optional[bool]
    justification: Optional[str]
    evidence: Optional[List[str]]
    edi: Optional[str]

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("extract", emr_extractor.review_and_extract_emr_data)
    graph.add_node("convert", code_agent.convert_to_CPT_ICD_modifier_bundle)
    graph.add_node("validate", validation_agent.check_payer_rules)
    graph.add_node("modify", modifier_agent.apply_risk_modifiers)
    graph.add_node("format", edi_formatter.format_to_edi_x12)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "convert")
    graph.add_edge("convert", "validate")
    graph.add_edge("validate", "modify")
    graph.add_edge("modify", "format")
    graph.set_finish_point("format")

    return graph.compile()
