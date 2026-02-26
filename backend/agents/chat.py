from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from backend.shared.config import settings
from backend.shared.database import db_manager
from backend.agents.interpreters import RiskInterpretationAgent, PreMeetingBriefAgent, DraftingAgent
import json

class ChatAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=600
        )
        # These are now thin wrappers around the deterministic IntelligenceWorkflow
        self.risk_agent = RiskInterpretationAgent()
        self.brief_agent = PreMeetingBriefAgent()
        self.draft_agent = DraftingAgent()
        
        self.system_prompt = """You are Atlas, a proactive UK Financial Advisory Intelligence Layer.
        Your goal is to help financial advisers manage their clients by providing proactive insights, 
        meeting briefs, and communication drafts.
        
        You have access to:
        1. Proactive Risk Events: Triggered by deterministic market/portfolio changes.
        2. Meeting Briefs: Preparation for upcoming client reviews.
        3. Draft Actions: Suggested communication to clients.
        
        When a user asks about a client, you can provide a summary or brief.
        When a user asks to interpret a risk, you use your specialized logic.
        
        Keep your tone professional, authoritative, and concise. 
        Always refer to yourself as Atlas.
        """

    async def get_response(self, message: str, history: List[Dict[str, str]] = None) -> str:
        # Simple routing logic (can be upgraded to full tool calling later)
        if "risk" in message.lower() or "analyze" in message.lower():
            # Attempt to find relevant risk event if not specified
            return "I am analyzing the latest volatility in the FTSE 100 relative to your clients' core weightings. One moment."
            
        elif "brief" in message.lower() or "prepare" in message.lower():
            return "I am gathering policy data, tax history, and behavioural memory to prepare your meeting brief."
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        chain = prompt | self.llm
        
        formatted_history = []
        if history:
            for m in history:
                if m["role"] == "user":
                    formatted_history.append(HumanMessage(content=m["content"]))
                else:
                    formatted_history.append(AIMessage(content=m["content"]))
                    
        response = await chain.ainvoke({
            "input": message,
            "history": formatted_history
        })
        
        return response.content
