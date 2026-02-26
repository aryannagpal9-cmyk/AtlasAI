from typing import Dict, Any, List, Optional
import json
from shared.config import settings
from reasoning.workflows import intelligence_workflow
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
        from mcp_server.main import get_client_portfolio_structure, get_tax_position, retrieve_relevant_memory
        
        portfolio = await get_client_portfolio_structure(client_id)
        tax = await get_tax_position(client_id)
        memories = await retrieve_relevant_memory(client_id, "meeting preparation")
        
        system_prompt = """
        You are Atlas, a Senior UK Financial Advisor. Prepare a highly detailed, comprehensive meeting brief. 
        You must analyze the client's portfolio, tax position, and behavioral memory to provide everything an advisor might need for this meeting.
        
        Output MUST be valid JSON with this exact structure:
        {
          "client_summary": "string (Detailed summary of the client's current standing, risk tolerance, and key identifiers)",
          "portfolio_performance": "string (How the portfolio is currently structured and performing)",
          "priority_strategic_talking_point": "string (The #1 most important topic to cover)",
          "proactive_thought": "string (High-level advisor-facing strategic summary for the meeting)",
          "key_asset_allocation": ["string (bullet points of significant holdings)"],
          "tax_opportunities": ["string (bullet points of ISA/Pension allowances remaining)"],
          "recent_life_events_or_memories": ["string (Summarized from their behavioral memory)"],
          "suggested_agenda_items": ["string"],
          "compliance_reminders": ["string (e.g., 'Ensure KYC is updated', 'Confirm Risk Profile')"]
        }
        """
        
        human_input = f"Client: {client_name}\nPortfolio: {json.dumps(portfolio)}\nTax: {json.dumps(tax)}\nMemory: {json.dumps(memories)}"
        
        response = await self.llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=human_input)])
        content = response.content
        import re
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        if json_match:
            clean = json_match.group(1)
        else:
            clean = content.strip().strip("```json").strip("```")
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
        from mcp_server.main import fetch_comprehensive_market_intel
        market_intel = await fetch_comprehensive_market_intel()
        return await intelligence_workflow.generate_morning_report(clients, market_intel)

class ProactiveVoiceAgent:
    """Agent that generates opinionated, proactive 'opening gambits' for Atlas."""
    def __init__(self):
        self.llm = ChatGroq(model=settings.groq_model, temperature=0.7, api_key=settings.groq_api_key)

    async def generate_voice(self, context_summary: str, event_type: str) -> str:
        """
        Generates a proactive prose response.
        Format: [Situation] -> [Belief] -> [Action/Question]
        """
        system_prompt = f"""
        You are Atlas, a senior UK Financial Advisory proactive brain.
        Your goal is to transform technical data into a proactive, intelligent opening gambit for an advisor.
        
        TONE: Professional, opinionated, proactive, concise.
        FORMAT: A single short paragraph (max 3 sentences).
        STRUCTURE: State the situation, your professional belief about it, and a clear suggested next step or question for the advisor.
        
        Context Type: {event_type}
        """
        
        human_input = f"Data Context:\n{context_summary}"
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt), 
                HumanMessage(content=human_input)
            ])
            return response.content.strip()
        except Exception as e:
            from shared.logging import setup_logger
            logger = setup_logger("interpreters")
            logger.error(f"Proactive voice generation failed: {e}")
            return ""
