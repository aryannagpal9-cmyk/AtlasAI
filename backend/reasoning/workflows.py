import json
import asyncio
from typing import Dict, Any, List, Optional
from backend.shared.logging import setup_logger
from backend.shared.database import db_manager
from backend.shared.config import settings
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = setup_logger("workflows")

class IntelligenceWorkflow:
    """
    Deterministic workflow that assembles context and invokes the LLM directly.
    Replaces autonomous agents with a cheaper, faster pipeline.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=0,
            api_key=settings.groq_api_key,
            max_tokens=1000
        )

    def _optimize_market_context(self, market_intel: Dict[str, Any]) -> str:
        """
        Optimizes context by extracting only high-signal headlines and indicators.
        Reduces token usage and noise.
        """
        if not market_intel:
            return "No market context available."
            
        indices = market_intel.get("indices", {})
        sectors = market_intel.get("sectors", {})
        news = market_intel.get("news_headlines", [])
        geo = market_intel.get("geopolitical_context", [])
        
        context_str = "Latest Market Intelligence:\n"
        if indices:
            context_str += f"- Indices: FTSE 100 ({indices.get('ftse_100')}), FTSE 250 ({indices.get('ftse_250')})\n"
        
        if sectors:
            perf_str = ", ".join([f"{s}: {v*100:+.1f}%" for s, v in sectors.items()])
            context_str += f"- Sector Performance: {perf_str}\n"
            
        if news:
            context_str += "- Key Headlines: " + " | ".join(news[:3]) + "\n"
            
        if geo:
            context_str += "- Geopolitical Context: " + " | ".join(geo[:2]) + "\n"
            
        return context_str

    async def interpret_risk(self, client_id: str, risk_event: dict, market_context: dict = None) -> dict:
        """
        Workflow for Risk Interpretation:
        1. Fetch client memory.
        2. Optimize market context.
        3. Single LLM call for a personalized headline.
        """
        # 1. Fetch relevant memory (Direct DB call, no agent search)
        memories_resp = db_manager.client.rpc(
            "match_memory",
            {
                "query_embedding": [0.0]*384, # Dummy for now, ideally we use the risk text
                "match_threshold": 0.4,
                "match_count": 3,
                "client_id_filter": client_id
            }
        ).execute()
        memories = [m["content"] for m in memories_resp.data] if memories_resp.data else ["No prior relevant behavioral history."]
        
        # 2. Optimize market context
        optimized_market = self._optimize_market_context(market_context)
        
        # 3. Assemble Prompt
        system_prompt = """
        You are Atlas, a Senior Financial Advisor Brain. Your job is to generate a punchy, personalized headline for a detected risk.
        
        Inputs: 
        - Deterministic Risk Finding: The technical reason.
        - Client Context: Past behavioral memory and goals.
        - Market Context: Current UK market environment.
        
        Goal: Articulate the strategic consequence. Be opinionated.
        
        Output MUST be a valid JSON object:
        {
          "headline": "string (Personalized high-signal headline)",
          "consequence_if_ignored": "string",
          "behavioural_nuance": "string",
          "suggested_action_type": "exactly 'draft_email' or 'dismiss'"
        }
        """
        
        human_input = f"""
        Risk Event: {json.dumps(risk_event)}
        Client Memory: {", ".join(memories)}
        {optimized_market}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_input)
            ])
            
            content = response.content
            # Use regex to find the JSON block in case there's conversational filler
            import re
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                clean_content = json_match.group(1)
            else:
                clean_content = content.strip().strip("```json").strip("```")
            
            if not clean_content:
                raise ValueError("Empty response content after cleaning")
                
            return json.loads(clean_content)
        except Exception as e:
            logger.error(f"Workflow interpretation failed: {e}. Raw content: {response.content if 'response' in locals() else 'N/A'}")
            return {
                "headline": f"Risk detected: {risk_event.get('event_type')}",
                "consequence_if_ignored": "Technical analysis required.",
                "behavioural_nuance": "N/A",
                "suggested_action_type": "dismiss",
                "error": str(e)
            }

    async def generate_morning_report(self, clients: List[Dict[str, Any]], market_context: Dict[str, Any]) -> dict:
        """
        Workflow for Morning Intelligence:
        1. Optimize global market context.
        2. Single LLM call to synthesize the book summary.
        """
        optimized_market = self._optimize_market_context(market_context)
        client_list = "\n".join([f"- {c['first_name']} {c['last_name']}: {c.get('vulnerability_category', 'Standard')}" for c in clients[:10]])
        
        system_prompt = """
        You are the Atlas Morning Intelligence Service. Provide a high-level summary of the UK market and the advisor's book.
        
        Output MUST be valid JSON:
        {
          "book_summary_card": { "title": "string", "bullets": ["string"] },
          "market_summary": "string",
          "critical_news": ["List of most urgent/critical news headlines"],
          "suggested_morning_actions": ["string"]
        }
        """
        
        human_input = f"""
        {optimized_market}
        Client Book Overview:
        {client_list}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_input)
            ])
            content = response.content
            import re
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                clean_content = json_match.group(1)
            else:
                clean_content = content.strip().strip("```json").strip("```")
            return json.loads(clean_content)
        except Exception as e:
            logger.error(f"Workflow morning report failed: {e}")
            return {"error": str(e)}

intelligence_workflow = IntelligenceWorkflow()
