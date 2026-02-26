from typing import Dict, Any, List, Optional
import json
from backend.shared.config import settings
from backend.reasoning.workflows import intelligence_workflow
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# We keep the prompts here for organization, but the workflow uses them or similar once.
# For simplicity, we can just export the workflow methods as the "agents".

class RiskInterpretationAgent:
    """Wrapper for backward compatibility, now using deterministic workflow."""
    async def interpret(self, client_id: str, risk_event: dict, market_context: dict = None) -> dict:
        return await intelligence_workflow.interpret_risk(client_id, risk_event, market_context)

class PreMeetingBriefAgent:
    """Streamlined meeting brief generator."""
    def __init__(self):
        self.llm = ChatGroq(model=settings.groq_model, temperature=0, api_key=settings.groq_api_key)

    async def generate_brief(self, client_id: str, client_name: str) -> dict:
        # Optimization: Fetch memory and portfolio structure once, then call LLM
        from backend.mcp_server.main import get_client_portfolio_structure, get_tax_position, retrieve_relevant_memory
        
        portfolio = await get_client_portfolio_structure(client_id)
        tax = await get_tax_position(client_id)
        memories = await retrieve_relevant_memory(client_id, "meeting preparation")
        
        system_prompt = """
        You are Atlas. Prepare a concise, professional meeting brief. 
        Focus on priority strategic talking points.
        Output JSON: { "client_summary": "string", "priority_strategic_talking_point": "string", ... }
        """
        
        human_input = f"Client: {client_name}\nPortfolio: {json.dumps(portfolio)}\nTax: {json.dumps(tax)}\nMemory: {json.dumps(memories)}"
        
        response = await self.llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=human_input)])
        clean = response.content.strip().strip("```json").strip("```")
        return json.loads(clean)

class DraftingAgent:
    """Streamlined drafting generator."""
    def __init__(self):
        self.llm = ChatGroq(model=settings.groq_model, temperature=0, api_key=settings.groq_api_key)

    async def generate_draft(self, client_id: str, risk_event: dict) -> dict:
        system_prompt = "You are Atlas. Draft a proactive, opinionated email for this risk. Output JSON: { 'subject': 'string', 'body': 'string' }"
        human_input = f"Risk: {json.dumps(risk_event)}"
        
        response = await self.llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=human_input)])
        clean = response.content.strip().strip("```json").strip("```")
        return json.loads(clean)

class MorningIntelligenceAgent:
    """Wrapper for backward compatibility, now using deterministic workflow."""
    async def generate_report(self, clients: list[dict]) -> dict:
        # Fetch market intel once
        from backend.mcp_server.main import fetch_comprehensive_market_intel
        market_intel = await fetch_comprehensive_market_intel()
        return await intelligence_workflow.generate_morning_report(clients, market_intel)

class MarketPulseAgent:
    """Simplified pulse check."""
    async def check_pulse(self, market_snapshot: dict) -> dict:
        # For a truly deterministic workflow, we can use simple rules or a single LLM call
        # For now, let's keep it very simple to reduce calls.
        return {"is_interrupt": False, "reason": "Stable"}
