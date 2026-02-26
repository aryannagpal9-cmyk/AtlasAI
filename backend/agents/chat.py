from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from shared.config import settings
from shared.database import db_manager
from shared.logging import setup_logger
from mcp_server.main import (
    search_market_news, 
    fetch_live_market_data, 
    get_client_portfolio_structure,
    get_tax_position,
    retrieve_relevant_memory
)
import json

logger = setup_logger("agents.chat")

class ChatAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=1000
        )
        
        from langchain.tools import tool

        @tool
        async def search_market_news_tool(query: str = "UK financial markets FTSE today", max_results: int = 5):
            """Search for latest UK financial market news and headlines."""
            return await search_market_news(query, max_results)
            
        @tool
        async def fetch_live_market_data_tool():
            """Fetch real-time UK market indices and sector performance."""
            return await fetch_live_market_data()
            
        @tool
        async def get_client_portfolio(client_id: str):
            """Get the detailed portfolio holdings and GBP value for a specific client_id."""
            return await get_client_portfolio_structure(client_id)
            
        @tool
        async def get_tax_position_tool(client_id: str):
            """Get a client's tax profile, allowances, and ISA/CGT positions for a client_id."""
            return await get_tax_position(client_id)
            
        @tool
        async def retrieve_client_memory(query: str, client_id: str = None):
            """Search past conversations and behavioural history for a client using a semantic query."""
            return await retrieve_relevant_memory(client_id, query)

        @tool
        def get_client_details(client_id: str):
            """Get basic client information, vulnerability status, and personal notes for a client_id."""
            return db_manager.get_by_id("clients", client_id)

        self.tools = [
            search_market_news_tool,
            fetch_live_market_data_tool,
            get_client_portfolio,
            get_tax_position_tool,
            retrieve_client_memory,
            get_client_details
        ]

        self.system_prompt = """You are Atlas, a senior UK Financial Advisory Intelligence agent.
        
        STRICT RULES:
        1. Use provided tools to fetch real data for specific clients.
        2. If a 'client_id' is in [CURRENT CONTEXT], use it for all tool calls.
        3. Never invent tools or IDs.
        4. If a tool fails or returns no data, explain that to the user.
        5. Tone: Professional, concise, UK finance expert.
        
        FORMATTING RULES:
        1. ALWAYS use Markdown to make your responses readable.
        2. Use **bolding** for key metrics, client names, and tickers.
        3. Use bullet points for lists of risks, actions, or holdings.
        4. Use horizontal rules (---) or headers to separate distinct sections (e.g., Market Context vs. Client Impact).
        5. Keep paragraphs short and scannable.
        
        DRAFT GENERATION & MEETING PREP:
        1. When context 'action' is 'generate_draft' (CLIENT COMMUNICATION):
           - Write a professional, empathetic email to the client.
           - Structure with **Subject:** and **Body:**.
           - Tone: Reassuring, external, proactive.
        2. When context 'action' is 'prepare_meeting' (ADVISOR BRIEFING):
           - Write an internal, tactical briefing for the financial advisor.
           - Focus on: Strategic Agenda, Key Alpha/Tax opportunities, potential client objections, and behavioral prep.
           - DO NOT use "Dear [Client]", use "Advisor Briefing: [Client]".
           - Tone: Strategic, internal, analytical.
        """

    async def stream_response(self, message: str, history: List[Dict[str, str]] = None, context: Dict[str, Any] = None):
        # Prepare the agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        # Enhance input with context if available
        input_text = message
        if context:
            ctx_str = f"\n\n[CURRENT CONTEXT]\n"
            if "client_id" in context:
                ctx_str += f"Current Client ID: {context['client_id']}\n"
            if "client_pname" in context:
                ctx_str += f"Current Client Name: {context['client_pname']}\n"
            if "risk_event_id" in context:
                ctx_str += f"Current Risk/Case ID: {context['risk_event_id']}\n"
            
            action = context.get("action")
            if action == "generate_draft":
                ctx_str += "ACTION: The advisor clicked 'Take Action' for a RISK. Generate a client communication draft.\n"
            elif action == "prepare_meeting":
                ctx_str += "ACTION: The advisor clicked 'Take Action' for a MEETING. Prepare an internal strategic briefing for the advisor.\n"
                
            input_text = ctx_str + input_text

        # Format history
        from langchain.schema import HumanMessage, AIMessage
        formatted_history = []
        if history:
            for m in history:
                if m["role"] == "user":
                    formatted_history.append(HumanMessage(content=m["content"]))
                else:
                    formatted_history.append(AIMessage(content=m["content"]))

        try:
            async for event in agent_executor.astream_events(
                {"input": input_text, "chat_history": formatted_history},
                version="v2"
            ):
                kind = event["event"]
                
                # Capture tool starts with friendly names
                if kind == "on_tool_start":
                    tool_name = event['name']
                    friendly_map = {
                        "search_market_news_tool": "Checking latest UK financial headlines...",
                        "fetch_live_market_data_tool": "Analyzing live FTSE performance and sector trends...",
                        "get_client_portfolio": f"Reviewing {context.get('client_pname', 'client')}'s specific portfolio and exposures...",
                        "get_tax_position_tool": "Calculating tax allowances and CGT positions...",
                        "retrieve_client_memory": "Searching behavioral patterns and past reactions...",
                        "get_client_details": "Reviewing vulnerability notes and advisory preferences..."
                    }
                    thought = friendly_map.get(tool_name, f"Thinking about {tool_name.replace('_', ' ')}...")
                    
                    yield json.dumps({
                        "type": "thought", 
                        "content": thought
                    }) + "\n"
                
                # Capture final answer chunks
                elif kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield json.dumps({
                            "type": "answer", 
                            "content": content
                        }) + "\n"

        except Exception as e:
            logger.error(f"Agent streaming error: {e}")
            yield json.dumps({
                "type": "error", 
                "content": str(e)
            }) + "\n"
